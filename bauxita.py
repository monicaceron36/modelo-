from flask import Flask, request, render_template
import pulp

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def bauxita():
    MINAS = ['A', 'B', 'C']
    PLALU = ['B', 'C', 'D', 'E']
    PLESM = ['D', 'E']

    capal_es = {'D': 4000, 'E': 7000}
    capb_al = {'B': 40000, 'C': 20000, 'D': 30000, 'E': 80000}
    capbaux = {'A': 36000, 'B': 52000, 'C': 28000}
    cexp = {'A': 420, 'B': 360, 'C': 540}
    cfijo = {'B': 3000000, 'C': 2500000, 'D': 4800000, 'E': 6000000}
    cpal = {'B': 330, 'C': 320, 'D': 380, 'E': 240}
    cpes = {'D': 8500, 'E': 5200}
    ctran_al = {('B','D'):220, ('B','E'):1510, ('C','D'):620, ('C','E'):940,
                ('D','D'):0, ('D','E'):1615, ('E','D'):1465, ('E','E'):0}
    ctran_b = {('A','B'):400, ('A','C'):2010, ('A','D'):510, ('A','E'):1920,
                ('B','B'):10,  ('B','C'):630,  ('B','D'):220, ('B','E'):1510,
                ('C','B'):1630,('C','C'):10,   ('C','D'):620, ('C','E'):940}
    demanda = {'D': 1000, 'E': 1200}
    rendal = {'A': 0.060, 'B': 0.080, 'C': 0.062}
    rendim = 0.4

    costo_total_minimo = None
    plantas_abiertas = ""

    if request.method == "POST":
        # Capturar valores ingresados por el usuario
        w_input = {j: int(request.form.get(f"w_{j}", 0)) for j in PLALU}
        print("Variables binarias ingresadas:", w_input)

        # Variables de decisión
        x = pulp.LpVariable.dicts("X", [(i,j) for i in MINAS for j in PLALU], lowBound=0)
        y = pulp.LpVariable.dicts("Y", [(j,k) for j in PLALU for k in PLESM], lowBound=0)

        # Modelo
        model = pulp.LpProblem("Problema_Bauxita", pulp.LpMinimize)

        # Función objetivo
        model += (
            pulp.lpSum(cexp[i]*x[(i,j)] for i in MINAS for j in PLALU) +
            pulp.lpSum(cpal[j]*y[(j,k)] for j in PLALU for k in PLESM) +
            pulp.lpSum(cpes[k]*y[(j,k)] for j in PLALU for k in PLESM) +
            pulp.lpSum(ctran_b[(i,j)]*x[(i,j)] for i in MINAS for j in PLALU) +
            pulp.lpSum(ctran_al[(j,k)]*y[(j,k)] for j in PLALU for k in PLESM) +
            pulp.lpSum(cfijo[j]*w_input[j] for j in PLALU)
        )

        # Restricciones
        for i in MINAS:
            model += pulp.lpSum(x[(i,j)] for j in PLALU) <= capbaux[i]

        for j in PLALU:
            model += pulp.lpSum(x[(i,j)] for i in MINAS) <= capb_al[j] * w_input[j]

        for k in PLESM:
            model += pulp.lpSum(y[(j,k)] for j in PLALU) <= capal_es[k]

        for k in PLESM:
            model += pulp.lpSum(rendim * y[(j,k)] for j in PLALU) == demanda[k]

        for j in PLALU:
            model += pulp.lpSum(rendal[i]*x[(i,j)] for i in MINAS) == pulp.lpSum(y[(j,k)] for k in PLESM)

        # Resolver
        model.solve(pulp.PULP_CBC_CMD(msg=False))

        # Resultados
        costo_total_minimo = pulp.value(model.objective)
        plantas_abiertas = ""
        for j in PLALU:
            plantas_abiertas += f"Planta {j}: {w_input[j]}\n"

    return render_template("bauxita.html",
                           costo_total_minimo=costo_total_minimo,
                           plantas_abiertas=plantas_abiertas)

if __name__ == "__main__":
    app.run(debug=True)