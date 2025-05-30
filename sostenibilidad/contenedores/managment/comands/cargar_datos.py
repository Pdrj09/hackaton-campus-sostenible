import requests
from django.core.management.base import BaseCommand
from contenedores.models import Contenedor, Centro
from django.http import JsonResponse

import datetime

url = "https://hackaton-campus-sostenible-api.mmartinez-d6a.workers.dev/containers/measurements"
headers = {
    "Authorization": "Bearer campus-sostenible-2025"
}

class obtener_niveles(BaseCommand):

    help = 'Carga los datos de los contenedores desde la API remota'
    
    def handle(self, *args, **kwargs):

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data_api = response.json()

            resultado = []

            for item in data_api:
                if Contenedor.objects.get(contenedorId = item["id"]).exists():
                    contenedor = Contenedor.objects.get(contenedorId=item["id"])
                    contenedor.historico_capacidades.append({
                        "fecha": datetime.strptime(item["date"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                        "nivel": item["level"]
                    })
                    contenedor.save()
                else:
                    if not Centro.objects.filter(id=item["centro"]).exists():
                        centro = Centro(
                            centro=item["center_name"]
                        )
                        centro.save()
                    else:
                        centro = Centro.objects.get(id=item["centro"])
                    contenedor = Contenedor(
                        contenedorId=item["id"],
                        tipo_contenedor=item["type"],
                        centro=Centro.objects.get(id=item["centro"]),
                        latitud=item["latitude"],
                        longitud=item["longitude"],
                        capacidad=item["capacity"],
                        unidades=item["units"],
                        fecha_instalacion=datetime.datetime.strptime(item["installation_date"], "%Y-%m-%d"),
                        historico_capacidades=[{
                            "fecha": datetime.datetime.strptime(item["date"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                            "nivel": item["level"]
                        }]
                    )
                    contenedor.save()

            return JsonResponse(resultado, safe=False)

        except requests.RequestException as e:
            return JsonResponse({"error": str(e)}, status=500)