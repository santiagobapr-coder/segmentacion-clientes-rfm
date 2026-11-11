# Segmentación de clientes (RFM) con plan de acción

Clasifica a los clientes de una tienda online según **qué tan recientemente compraron (R), con qué
frecuencia (F) y cuánto gastaron (M)**, y entrega lo que el dueño realmente necesita: *a quién cuidar,
a quién recuperar y a quién dejar de perseguir*.

## Qué incluye

- 7 segmentos de clientes: Campeones, Leales, Nuevos, Por activar, En riesgo, Valiosos dormidos y Dormidos.
- Peso de cada segmento en clientes y en ingresos.
- Mapa de recencia × frecuencia y curva de concentración de ingresos (el 20% de clientes aporta casi la mitad).
- **Plan de acción** con una recomendación distinta para cada segmento.
- `clientes_rfm.csv`: lista de cada cliente con su segmento, lista para usar en campañas.

## Cómo se segmenta

| Variable | Cómo se mide |
| --- | --- |
| R (recencia) | Días desde la última compra, en quintiles (5 = compró hace poco) |
| F (frecuencia) | Número de pedidos: 1, 2 o 3 o más |
| M (monto) | Gasto total, en quintiles |

Las reglas de cada segmento están en la función `segmento()` de `rfm.py` y se pueden ajustar al negocio.

## Uso

```bash
pip install -r requirements.txt
python rfm.py
```

`ventas.csv` es el mismo archivo de ventas inventadas del proyecto 1. Para datos reales, usa las columnas
`order_id, fecha, cliente_id, cantidad, precio_unitario, descuento`.

## Tecnologías

Python, pandas, numpy, matplotlib, HTML/CSS.

> Datos inventados. Los porcentajes y montos que aparecen salen de esos datos de ejemplo, no de un negocio real.


## Qué busca (el problema)

Se trata igual a todos los clientes; los mejores se van sin aviso.

## Cómo se cumple

Segmenta por recencia, frecuencia y valor en 7 grupos con plan de acción (campeones, en riesgo, dormidos...).

## Cómo ofrecerlo como servicio

- **Qué entrego:** Análisis RFM de tu base de clientes + lista de a quién escribirle y qué ofrecerle.
- **A quién:** Tiendas, gimnasios y negocios con clientes recurrentes.
- **Precio de referencia (ajustar):** Análisis único: 300.000–900.000 COP. Repetición trimestral: 150.000–300.000 COP.
- **Frase para empezar:** «Te entrego la lista de tus mejores clientes y de los que están a punto de irse.»
- **Flujo:** 1) reunión corta y datos del cliente → 2) prototipo con sus datos → 3) ajustes → 4) entrega y capacitación.

> Datos del repositorio inventados; ejecutar los scripts para reproducir el tablero.

> Para generar `ventas.csv` de ejemplo ejecuta primero `python generate_data.py` (datos inventados).
