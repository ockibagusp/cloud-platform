from pymongo import MongoClient
from bson.objectid import ObjectId


class SensordatasService:
    def __init__(self):
        self.server_address = ""

    def getbyuser(self, request):
        client = MongoClient('192.168.56.101', 27017)
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

        queryset_count = db.sensordatas.count({"node": {"$in": tmp}})

        pages = queryset_count / 10

        if pages < page or page == 0:
            return {
                "detail": "Invalid page."
            }

        if filter_from and filter_last:
            queryset = db.sensordatas.find({"node": {"$in": tmp}}, timestamp__gte=filter_from, timestamp__lte=filter_last)
        elif filter_from:
            queryset = db.sensordatas.find({"node": {"$in": tmp}}, timestamp__gte=filter_from)
        elif filter_last:
            queryset = db.sensordatas.find({"node": {"$in": tmp}}, timestamp__lte=filter_last)
        else:
            queryset = db.sensordatas.find({"node": {"$in": tmp}})

        return {
            "count": queryset_count,
            "next": "null" if page >= pages else resource_address + "?page=" + str(page + 1),
            "previous": "null" if 1 == page else resource_address + "?page=" + str(page - 1),
            "results": self.parsetojson(queryset.skip(page - 1).limit(10))
        }

    def parsetojson(self, raw_data):
        data = []
        for d in list(raw_data):
            new = {
                "id": str(d.get("_id")),
                "node": str(d.get("node")),
                "url": self.server_address + "/sensordatas/" + str(d.get("_id")),
                "nodeurl": self.server_address + "/nodes/" + str(d.get("node")),
                "sensorurl": self.server_address + "/nodes/" + str(d.get("node")) + "/" + str(d.get("sensor")),
                "sensor": str(d.get("sensor")),
                "timestamp": str(d.get("timestamp")),
                "data": d.get("data")
            }
            data.append(new)
        return data
