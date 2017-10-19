from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime


class SensordatasService:
    def __init__(self):
        self.server_address = ""

    def getbyuser(self, request):
        client = MongoClient('localhost', 27017)
        db = client.agrihub
        user_id = ObjectId(request.user.id)
        self.server_address = request.get_host()
        resource_address = self.server_address + "/sensordatas/user/" + request.user.username + "/"
        page = 1 if not request.GET.get('page') else int(request.GET.get('page'))
        filter_from = request.GET.get('start')
        filter_last = request.GET.get('end')

        pipeline = [
            {"$match": {"user": user_id}},
            {
                "$lookup": {
                    "from": "user",
                    "localField": "user",
                    "foreignField": "_id",
                    "as": "embeddedDocument"
                }
            },
            {"$project": {"_id": 1}}
        ]

        cursor = db.nodes.aggregate(pipeline=pipeline)

        tmp = []

        for d in list(cursor):
            tmp.append(d.get("_id"))

        if 1 > page:
            return {
                "detail": "Invalid page."
            }

        pipeline = [
            {
                "$lookup": {
                    "from": "nodes",
                    "localField": "node",
                    "foreignField": "_id",
                    "as": "node_object"
                }
            }, {
                "$match": {
                    "$and": [
                        {"node": {"$in": tmp}}
                    ]
                }
            },
            {"$skip": page-1},
            {"$limit": 10}
        ]

        pipeline_count = {"node": {"$in": tmp}}

        if filter_from and filter_last:
            query = {
                "timestamp": {
                    "$gte": datetime.strptime(filter_from, "%Y-%m-%d %H:%M"),
                    "$lte": datetime.strptime(filter_last, "%Y-%m-%d %H:%M")
                }
            }
            pipeline[1]["$match"]["$and"].append(query)
            pipeline_count.update(query)
        elif filter_from:
            query = {
                "timestamp": {
                    "$gte": datetime.strptime(filter_from, "%Y-%m-%d %H:%M")
                }
            }
            pipeline[1]["$match"]["$and"].append(query)
            pipeline_count.update(query)
        elif filter_last:
            query = {
                "timestamp": {
                    "$lte": datetime.strptime(filter_last, "%Y-%m-%d %H:%M")
                }
            }
            pipeline[1]["$match"]["$and"].append(query)
            pipeline_count.update(query)
        queryset = db.sensordatas.aggregate(pipeline=pipeline)
        queryset_count = db.sensordatas.count(pipeline_count)
        pages = queryset_count / 10

        return {
            "count": queryset_count,
            "next": "null" if (1 >= pages or page > pages) else resource_address + "?page=" + str(page + 1),
            "previous": "null" if 1 == page else resource_address + "?page=" + str(page - 1),
            "results": self.parsetojson(queryset)
        }

    def parsetojson(self, raw_data):
        data = []
        sensor_label = ""
        for d in list(raw_data):
            for s in d.get("node_object")[0].get("sensors"):
                if s.get("id") == d.get("sensor"):
                    sensor_label = str(s.get("label"))
            new = {
                "id": str(d.get("_id")),
                "node": str(d.get("node")),
                "nodelabel": d.get("node_object")[0].get("label"),
                "url": self.server_address + "/sensordatas/" + str(d.get("_id")),
                "nodeurl": self.server_address + "/nodes/" + str(d.get("node")),
                "sensorurl": self.server_address + "/nodes/" + str(d.get("node")) + "/" + str(d.get("sensor")),
                "sensor": str(d.get("sensor")),
                "sensorlabel": sensor_label,
                "timestamp": str(d.get("timestamp")),
                "data": d.get("data")
            }
            data.append(new)
        return data
