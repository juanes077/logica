
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict, Any
import re
import json
import os
from datetime import datetime


class ConcesionarioError(Exception):



class SeleccionInvalidaError(ConcesionarioError):


class DiaNoDisponibleError(ConcesionarioError):


class PersistenciaError(ConcesionarioError):


class Vehiculo(ABC):

    @abstractmethod
    def mostrar_informacion(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def mostrar_resumen(self, indice: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def performance_score(self) -> float:
        raise NotImplementedError


@dataclass
class Moto(Vehiculo):
    id: int
    nombre: str
    marca: str
    precio: int
    motor: str
    potencia: str
    peso: int
    tipo: str

    def mostrar_informacion(self) -> None:
        print(f"\n--- Información de la {self.nombre} ---")
        print(f"ID: {self.id}")
        print(f"Marca: {self.marca}")
        print(f"Precio: ${self.precio:,}")
        print(f"Motor: {self.motor}")
        print(f"Potencia: {self.potencia}")
        print(f"Peso: {self.peso} kg")
        print(f"Tipo: {self.tipo}")
        print("--------------------------------------")

    def mostrar_resumen(self, indice: int) -> None:
        print(f"{indice}. [{self.id}] {self.nombre} ({self.marca}) - ${self.precio:,}")

    def potencia_num(self) -> Optional[float]:
        m = re.search(r"(\d+(\.\d+)?)", str(self.potencia))
        return float(m.group(1)) if m else None

    def performance_score(self) -> float:
        p = self.potencia_num() or 0.0
        power_factor = p / max(1.0, self.peso)
        score = power_factor * 100
        return score


@dataclass
class Cliente:
    nombre: str
    cedula: str
    telefono: str
    correo: str

    def mostrar_datos(self) -> None:
        print(f"\nCliente: {self.nombre}")
        print(f"Cédula: {self.cedula}")
        print(f"Teléfono: {self.telefono}")
        print(f"Correo: {self.correo}")


class CatalogoRepository:
    def __init__(self, path: str = "base_datos.json"):
        self.path = path
        self._catalogo: List[Moto] = []
        self.load()

    def load(self) -> None:
        if not os.path.exists(self.path):
            self._catalogo = []
            return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            self._catalogo = []
            for i, entry in enumerate(raw, start=1):
                if "id" not in entry:
                    entry["id"] = i
                self._catalogo.append(Moto(**entry))
        except Exception as e:
            raise PersistenciaError(f"Error leyendo JSON: {e}")

    def save(self) -> None:
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump([asdict(m) for m in self._catalogo], f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise PersistenciaError(f"Error guardando JSON: {e}")

    def list_all(self) -> List[Moto]:
        return list(self._catalogo)

    def get_by_id(self, moto_id: int) -> Moto:
        for m in self._catalogo:
            if m.id == moto_id:
                return m
        raise SeleccionInvalidaError(f"Moto con id {moto_id} no encontrada.")

    def get_by_index(self, index: int) -> Moto:
        if not (0 <= index < len(self._catalogo)):
            raise SeleccionInvalidaError("Índice fuera de rango.")
        return self._catalogo[index]

    def add(self, moto: Moto) -> None:
        self._catalogo.append(moto)
        self.save()

    def delete(self, moto_id: int) -> None:
        self._catalogo = [m for m in self._catalogo if m.id != moto_id]
        self.save()


class PruebaManejo:
    def __init__(self):
        self.disponibilidad = {d: True for d in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]}
        self.reservas: List[Tuple[Cliente, Moto, str]] = []

    def reservar_prueba(self, dia: str, cliente: Cliente, moto: Moto) -> None:
        dia = dia.capitalize()
        if dia not in self.disponibilidad:
            raise DiaNoDisponibleError(f"Día '{dia}' inválido.")
        if not self.disponibilidad[dia]:
            raise DiaNoDisponibleError(f"El día '{dia}' ya está ocupado.")
        self.disponibilidad[dia] = False
        self.reservas.append((cliente, moto, dia))
        print(f"\nPrueba de manejo reservada para {cliente.nombre} el {dia} con la moto {moto.nombre}.")


class Compra:
    def __init__(self):
        self.compras: List[Tuple[Cliente, Moto, str]] = []
        self.archivo_general = "compras.json"
        self.carpeta_recibos = "recibos"
        os.makedirs(self.carpeta_recibos, exist_ok=True)

    def realizar_pago(self, cliente: Cliente, moto: Moto, metodo_pago: str) -> None:
        print(f"\nProcesando compra de la {moto.nombre} por parte de {cliente.nombre}...")
        print(f"Método de pago: {metodo_pago}")
        print(f"Monto: ${moto.precio:,}")
        print("Pago completado exitosamente.")

        self.compras.append((cliente, moto, metodo_pago))
        self._guardar_compra(cliente, moto, metodo_pago)
        self._generar_recibo(cliente, moto, metodo_pago)

    def _guardar_compra(self, cliente, moto, metodo):
        compra_entry = {
            "cliente": asdict(cliente),
            "moto": asdict(moto),
            "metodo": metodo,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        data = []
        if os.path.exists(self.archivo_general):
            try:
                with open(self.archivo_general, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = []
        data.append(compra_entry)
        with open(self.archivo_general, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _generar_recibo(self, cliente, moto, metodo):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        recibo = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cliente": asdict(cliente),
            "moto": asdict(moto),
            "metodo": metodo
        }
        nombre_recibo = f"recibo_{cliente.cedula}_{moto.id}_{timestamp}.json"
        ruta_recibo = os.path.join(self.carpeta_recibos, nombre_recibo)
        with open(ruta_recibo, "w", encoding="utf-8") as f:
            json.dump(recibo, f, ensure_ascii=False, indent=2)


class Concesionario:
    def __init__(self, json_path: str = "base_datos.json"):
        self.repo = CatalogoRepository(json_path)
        self.pruebas = PruebaManejo()
        self.compras = Compra()

    def listar_motos(self) -> List[Moto]:
        return self.repo.list_all()

    def realizar_compra(self, cliente: Cliente, moto: Moto, metodo: str):
        self.compras.realizar_pago(cliente, moto, metodo)

    def reservar_prueba(self, dia, cliente, moto):
        self.pruebas.reservar_prueba(dia, cliente, moto)