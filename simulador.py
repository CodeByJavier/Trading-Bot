"""
Cartera de dinero ficticio. Simula compras y ventas con comisiones reales,
pero nunca toca dinero de verdad.
"""


class Cartera:
    def __init__(self, euros, comision_fija, comision_porcentaje, spread):
        self.euros = euros
        self.cantidad = 0.0  # cripto que tenemos
        self.comision_fija = comision_fija
        self.comision_porcentaje = comision_porcentaje
        self.spread = spread
        self.comisiones_pagadas = 0.0
        self.coste_ultima_compra = 0.0
        self.operaciones = []

    @property
    def en_posicion(self):
        return self.cantidad > 0

    def comprar(self, precio, fecha):
        if self.en_posicion or self.euros <= self.comision_fija * 2:
            return None
        invertido = self.euros - self.comision_fija
        comision = self.comision_fija + invertido * self.comision_porcentaje
        self.cantidad = invertido * (1 - self.comision_porcentaje) / (precio * (1 + self.spread))
        self.coste_ultima_compra = self.euros
        self.comisiones_pagadas += comision
        self.euros = 0.0
        operacion = {"tipo": "COMPRA", "fecha": fecha, "precio": precio,
                     "cantidad": self.cantidad, "euros": self.coste_ultima_compra,
                     "comision": comision, "resultado": None}
        self.operaciones.append(operacion)
        return operacion

    def vender(self, precio, fecha):
        if not self.en_posicion:
            return None
        bruto = self.cantidad * precio * (1 - self.spread)
        comision = self.comision_fija + bruto * self.comision_porcentaje
        neto = bruto - comision
        operacion = {"tipo": "VENTA", "fecha": fecha, "precio": precio,
                     "cantidad": self.cantidad, "euros": neto, "comision": comision,
                     "resultado": neto - self.coste_ultima_compra}
        self.comisiones_pagadas += comision
        self.euros += neto
        self.cantidad = 0.0
        self.operaciones.append(operacion)
        return operacion

    def valor(self, precio):
        """Lo que valdría la cartera si lo vendiéramos todo ahora mismo."""
        if not self.en_posicion:
            return self.euros
        bruto = self.cantidad * precio * (1 - self.spread)
        return self.euros + bruto - self.comision_fija - bruto * self.comision_porcentaje

    def a_dict(self):
        return dict(self.__dict__)

    @classmethod
    def desde_dict(cls, datos):
        cartera = cls(0, 0, 0, 0)
        cartera.__dict__.update(datos)
        return cartera


def valor_comprar_y_mantener(capital, precio_inicio, precio_actual, comision_fija, spread):
    """Referencia: comprar al principio y no hacer nada más (con las mismas comisiones)."""
    cantidad = (capital - comision_fija) / (precio_inicio * (1 + spread))
    return cantidad * precio_actual * (1 - spread) - comision_fija


def decidir(probabilidad_subida, en_posicion, umbral_compra, umbral_venta):
    if not en_posicion and probabilidad_subida >= umbral_compra:
        return "comprar"
    if en_posicion and probabilidad_subida < umbral_venta:
        return "vender"
    return None
