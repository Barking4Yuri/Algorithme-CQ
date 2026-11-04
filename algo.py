import csv
import sqlite3

class produit:

    def __init__(self, id: int, name : str, description : str, price : float, stock : int, promotion = 1):
        self._id = id
        self._name = name
        self._description = description
        self._stock = stock
        self._ref_price = price
        self._promotion = promotion
        self._price = self._ref_price * self._promotion

    def _dict_(self):
        dico = dict()
        dico["id"] = self._id
        dico["name"] = self._name
        dico["description"] = self._description
        dico["ref_price"] = self._ref_price
        dico["promotion"] = self._promotion
        dico["price"] = self._price
        dico["stock"] = self._stock
        return dico

    def get_produit(self):
        return self._dict_()

    def set_produit(self, id = None, name = None, description = None, price = None, stock = None, promotion = None):
        params = {
        "_id": id,
        "_name": name,
        "_description": description,
        "_ref_price": price,
        "_stock": stock,
        "_promotion": promotion
    }

        for attr, value in params.items():
            if value is not None:
                setattr(self, attr, value)

        self._price = self._ref_price * self._promotion

    def __str__(self):
        return f"Le produit {self._name} est le numéro {self._id}, son prix est de {self._price} et son le stock actuel est de {self._stock}"