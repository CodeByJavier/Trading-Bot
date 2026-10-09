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


def respetar_permanencia(accion, velas_desde_compra, minimo):
    """No deja vender antes de `minimo` velas desde la compra (evita comprar y vender sin parar)."""
    if accion == "vender" and velas_desde_compra is not None and velas_desde_compra < minimo:
        return None
    return accion


def decidir(probabilidad_subida, en_posicion, umbral_compra, umbral_venta,
            estrategia="ia", tendencia_alcista=None):
    """Devuelve "comprar", "vender" o None según la estrategia.

    - "ia":           según la probabilidad del cerebro.
    - "tendencia":    regla sin IA: dentro con tendencia alcista, fuera con bajista.
    - "tendencia_ia": compra solo si hay tendencia alcista Y el cerebro está de acuerdo;
                      vende si la tendencia se rompe o el cerebro deja de estarlo.
    """
    if estrategia == "tendencia":
        quiere_estar = tendencia_alcista
    elif estrategia == "tendencia_ia":
        if not en_posicion:
            quiere_estar = tendencia_alcista and probabilidad_subida >= umbral_compra
        else:
            quiere_estar = tendencia_alcista and probabilidad_subida >= umbral_venta
    elif estrategia == "ia":
        if not en_posicion:
            quiere_estar = probabilidad_subida >= umbral_compra
        else:
            quiere_estar = probabilidad_subida >= umbral_venta
    else:
        raise ValueError(f"Estrategia desconocida: {estrategia}")

    if quiere_estar and not en_posicion:
        return "comprar"
    if not quiere_estar and en_posicion:
        return "vender"
    return None
