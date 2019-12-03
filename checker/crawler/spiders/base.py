# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Filename: base
# @Date: 2019-11-29-17-02
# @Author: Nuullll (Yilong Guo)
# @Email: vfirst218@gmail.com

from requests_html import HTMLSession
from checker.util import today
import json

TODAY = today()


class Spider(object):
    """
    Base spider.
    """

    server_name = ''
    server_url = ''
    fields = []
    js_support = False
    collection = None

    @staticmethod
    def get_page(url, js_support=False):
        session = HTMLSession()
        r = session.get(url)

        if js_support:
            r.html.render(wait=5.0, timeout=15.0)

        if r.status_code == 200:
            return True, r.html

        return False, None

    @classmethod
    def get_user_url(cls, username):
        return cls.server_url.format(username)

    @classmethod
    def parse_fields(cls, context):
        data = {}

        for field in cls.fields:
            if field.xpath_selector:
                raw = context.xpath(field.xpath_selector)

                try:
                    cleaned = field.cleaner(raw[0])
                    data[field.name] = cleaned
                except IndexError as e:
                    print("WARNING: Failed to retrieve Field [{}] ({})".format(field.name, e))
            else:
                obj = json.loads(context.text)

                try:
                    cleaned = field.json_parser(obj)
                    data[field.name] = cleaned
                except KeyError as e:
                    print("WARNING: Failed to retrieve Field [{}] ({})".format(field.name, e))

        return data

    @classmethod
    def process_user(cls, username):
        url = cls.get_user_url(username)

        ok, context = cls.get_page(url, cls.js_support)

        if ok:
            data = cls.parse_fields(context)
            print("[{}@{}]: {}".format(username, cls.server_name, data))
            if data == {}:
                raise FileNotFoundError("ID error or Network error. No data was retrieved.")

            return data
        else:
            print("WARNING: Failed to get profile of [{}]".format(username))

        return {}
