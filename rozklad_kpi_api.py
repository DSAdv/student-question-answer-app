import requests
import json


class AbstractEndpoint:

    url_base: str = "http://api.rozklad.org.ua/v2/"
    url: str = None

    class Field:
        pass

    @staticmethod
    def build_filter_params(**kwargs):
        return {"filter": kwargs}

    @classmethod
    def get_url(cls):
        return cls.url

    @classmethod
    def get(cls, params: dict, url: str = None) -> dict:
        url_ = cls.get_url() if not url else url
        return requests.get(
            url_, params=params
        ).json()


class Group(AbstractEndpoint):

    url = AbstractEndpoint.url_base + "groups"

    class Field(AbstractEndpoint.Field):
        id = "group_id"
        full_name = "group_full_name"
        okr = "group_okr"
        type = "group_type"
        schedule_url = "group_url"

    def get_group_by_id(self, group_id: str):
        url = self.get_url() + "/" + str(group_id)
        return self.get(
            params={},
            url=url
        )

    def search_group(self, query: str):
        params = {
            "search": json.dumps({"query": query})
        }
        return self.get(
            params=params
        )


if __name__ == '__main__':
    group_api = Group()
    # print(requests.get("http://api.rozklad.org.ua/v2/groups/", params={"search": "{'query': 'тв'}"}).json())
    print(group_api.search_group("тв-51"))
    # print(Group.get(
    #     Group.build_filter_params(limit=100, offset=0)
    # ))