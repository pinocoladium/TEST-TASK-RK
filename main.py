import ftplib
import json
import logging

import psycopg2
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import User


class SelectDateModelsClass:
    """
    Класс для получения данных через модели
    """

    def __init__(self, credentials: dict):
        self.credentials = self.validation_credentials(credentials)

    def _create_engine(self):
        url = (
            f'{self.credentials["dialect"]}://{self.credentials["user"]}:'
            f'{self.credentials["password"]}@{self.credentials["host"]}/{self.credentials["dbname"]}'
        )
        engine = create_engine(url)
        return engine

    def select_data(self, model, filter=None):
        with Session(bind=self._create_engine()) as session:
            if self.validation_filter(filter):
                return [tuple(el) for el in session.query(model).filter(filter).all()]
            return [tuple(el) for el in session.query(model).all()]

    @staticmethod
    def validation_credentials(credentials):
        mandatory_cred = ["dialect", "user", "password", "host", "dbname"]
        if isinstance(credentials, dict):
            for cred in mandatory_cred:
                try:
                    credentials[cred]
                except:
                    raise Exception(f"Не указан {cred} для доступа к БД")
            if credentials.get("driver"):
                credentials["dialect"] = (
                    credentials["dialect"] + f'+{credentials.pop("driver")}'
                )
            return credentials
        raise TypeError(f"{credentials} - должен быть в формате dict")

    @staticmethod
    def validation_filter(filter):
        if isinstance(filter, sqlalchemy.sql.elements.BinaryExpression):
            return True
        elif filter:
            raise Exception("Неверный формат указанных фильтров")


class SelectDateSqlClass:
    """
    Класс для запросов через SQL запрос
    """

    def __init__(self, credentials: dict):
        self.credentials = self.validation_credentials(credentials)

    def select_data(self, query, value=None):
        connection = psycopg2.connect(**self.credentials)
        cursor = connection.cursor()
        query = self.validation_query(query, value)
        if value:
            cursor.execute(query, self.validation_value(value))
        else:
            cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        return data

    @staticmethod
    def validation_value(value):
        if value:
            if isinstance(value, tuple):
                return value
            raise TypeError(f"Значение {value} должно быть в формате - (значение,)")

    @staticmethod
    def validation_query(query, value):
        if "where" in query.lower() and not value:
            raise Exception(
                f"При использовании фильтрации в запросе необходимо указать value"
            )
        return query

    @staticmethod
    def validation_credentials(credentials):
        result = {}
        mandatory_cred = ["user", "password", "host", "dbname", "port"]
        if isinstance(credentials, dict):
            for cred in mandatory_cred:
                try:
                    result[cred] = credentials[cred]
                except:
                    raise Exception(f"Не указан {cred} для доступа к БД")
            return result
        raise TypeError(f"{credentials} - должен быть в формате dict")


class RecordJsonClass:
    """
    Класс для записи данных в json файл
    """

    def _pre_processing(self, data, keys):
        result = []
        if isinstance(keys, (tuple, list)):
            for el in data:
                res = {}
                if len(keys) != len(el):
                    logging.error(f"Переданные ключи не сходятся с элементом {el}")
                    continue
                for index, key in enumerate(keys):
                    res[key] = str(el[index])
                result.append(res)
            return result
        raise Exception("Ключи должны быть переданы в формате tuple или list")

    def record(self, data, file_name, keys: tuple):
        file_name = f"{file_name}.json"
        try:
            with open(file_name, "w") as f:
                json.dump(self._pre_processing(data, keys), f, indent=4)
            return file_name
        except Exception as e:
            raise Exception(e)


class FTPServerClass:
    """
    Класс загрузки файла на FTP сервер
    """

    def __init__(self, host_credentials: dict):
        self.host_credentials = self.validation_host_credentials(host_credentials)

    def download(self, path_file):
        ftp = ftplib.FTP(self.credentials["host"])
        ftp.login(
            user=self.credentials["username"], passwd=self.credentials["password"]
        )
        with open(path_file, "rb") as file:
            try:
                ftp.storbinary(f"STOR {path_file}", file)
            except Exception as e:
                raise Exception(e)

    @staticmethod
    def validation_host_credentials(host_credentials):
        mandatory_cred = ["host", "username", "password"]
        if isinstance(host_credentials, dict):
            for cred in mandatory_cred:
                try:
                    host_credentials[cred]
                except:
                    raise Exception(f"Не указан {cred} для доступа к FTP серверу")
            return
        raise TypeError(f"{host_credentials} - должен быть в формате dict")


if __name__ == "__main__":

    creds = {
        "dialect": "postgresql",
        "driver": "psycopg2",
        "user": "admin",
        "password": "admin",
        "host": "localhost",
        "dbname": "db",
        "port": 5432,
    }

    keys = [
        "id",
        "username",
        "email",
        "password",
        "date_created",
        "admin",
        "phone",
        "point",
    ]

    host_creds = {"host": "localhost", "username": "root", "password": "grvrgvbmjm56"}

    # s = SelectDateModelsClass(creds)
    # e = s.select_data(User, User.id != 2)

    s = SelectDateSqlClass(creds)
    e = s.select_data("SELECT * from auth_user WHERE id > %s", (1,))

    records = RecordJsonClass()
    file = records.record(e, "result", keys)

    ftp = FTPServerClass(host_creds)
    ftp.download(file)
