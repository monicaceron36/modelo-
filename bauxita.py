from flask import Flask, render_template, request
import pulp

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])

def home():
    salida_flask = ''
    
    if request.method == "POST":
        demanda_es_d= int(request.form.get("demanda_es_d"))
        demanda_es_e= int(request.form.get("demanda_es_e"))
        capacidad_es_d = int(request.form.get("capacidad_es_d"))
   
        # ----------------------------
        # Definición de conjuntos
        # ----------------------------
        MINAS = ['A', 'B', 'C']
        PLALU = ['B', 'C', 'D', 'E']
        PLESM = ['D', 'E']

        # ----------------------------
        # Parámetros
        # ----------------------------
        capal_es = {'D': capacidad_es_d, 'E': 7000}  # capacidad esmaltado (ton alúmina)
        capb_al = {'B': 40000, 'C': 20000, 'D': 30000, 'E': 80000}  # capacidad bauxita -> alúmina
        capbaux = {'A': 36000, 'B': 52000, 'C': 28000}  # capacidad minas

        cexp = {'A': 420, 'B': 360, 'C': 540}  # costo explotación
        cfijo = {'B': 3000000, 'C': 2500000, 'D': 4800000, 'E': 6000000}  # costo fijo plantas
        cpal = {'B': 330, 'C': 320, 'D': 380, 'E': 240}  # costo de producción alúmina
        cpes = {'D': 8500, 'E': 5200}  # costo procesamiento esmaltado

        ctran_al = {('B','D'):220, ('B','E'):1510, ('C','D'):620, ('C','E'):940,
                    ('D','D'):0, ('D','E'):1615, ('E','D'):1465, ('E','E'):0}

        ctran_b = {('A','B'):400, ('A','C'):2010, ('A','D'):510, ('A','E'):1920,
                    ('B','B'):10,  ('B','C'):630,  ('B','D'):220, ('B','E'):1510,
                    ('C','B'):1630,('C','C'):10,   ('C','D'):620, ('C','E'):940}

        #demanda = {'D': 1000, 'E': 1200}  # ton aluminio terminado/año
        demanda = {'D': demanda_es_d, 'E': demanda_es_e}
        
        rendal = {'A': 0.060, 'B': 0.080, 'C': 0.062}  # rendimiento bauxita->alúmina
        rendim = 0.4  # rendimiento alúmina->aluminio

        # ----------------------------
        # Variables de decisión
        # ----------------------------
        x = pulp.LpVariable.dicts("X", [(i,j) for i in MINAS for j in PLALU], lowBound=0)
        y = pulp.LpVariable.dicts("Y", [(j,k) for j in PLALU for k in PLESM], lowBound=0)
        w = pulp.LpVariable.dicts("W", PLALU, cat='Binary')

        # ----------------------------
        # Modelo
        # ----------------------------
        model = pulp.LpProblem("Problema_Bauxita", pulp.LpMinimize)

        # ----------------------------
        # Función Objetivo
        # ----------------------------
        model += (
            pulp.lpSum(cexp[i]*x[(i,j)] for i in MINAS for j in PLALU) +
            pulp.lpSum(cpal[j]*y[(j,k)] for j in PLALU for k in PLESM) +
            pulp.lpSum(cpes[k]*y[(j,k)] for j in PLALU for k in PLESM) +
            pulp.lpSum(ctran_b[(i,j)]*x[(i,j)] for i in MINAS for j in PLALU) +
            pulp.lpSum(ctran_al[(j,k)]*y[(j,k)] for j in PLALU for k in PLESM) +
            pulp.lpSum(cfijo[j]*w[j] for j in PLALU)
        )

        # ----------------------------
        # Restricciones
        # ----------------------------

        # Capacidad minas
        for i in MINAS:
            model += pulp.lpSum(x[(i,j)] for j in PLALU) <= capbaux[i], f"Cap_Mina_{i}"

        # Capacidad plantas de alúmina
        for j in PLALU:
            model += pulp.lpSum(x[(i,j)] for i in MINAS) <= capb_al[j]*w[j], f"Cap_Alumina_{j}"

        # Capacidad plantas de esmaltado
        for k in PLESM:
            model += pulp.lpSum(y[(j,k)] for j in PLALU) <= capal_es[k], f"Cap_Esmaltado_{k}"

        # Demanda de aluminio
        for k in PLESM:
            model += pulp.lpSum(rendim * y[(j,k)] for j in PLALU) == demanda[k], f"Demanda_{k}"

        # Balance de masa
        for j in PLALU:
            model += pulp.lpSum(rendal[i]*x[(i,j)] for i in MINAS) == pulp.lpSum(y[(j,k)] for k in PLESM), f"Balance_{j}"

        # ----------------------------
        # Resolver
        # ----------------------------
        model.solve(pulp.PULP_CBC_CMD(msg=False))

        # ----------------------------
        # Resultados
        # ----------------------------
        model.solve() #instruccion para resolver el modelo

        costo_total_minimo = pulp.value(model.objective)
        salida_costo = f"Costo total mínimo es: ${costo_total_minimo:,.0f}\n\n"

        plantas_abiertas = "Plantas de alúmina abiertas:\n"
        for j in PLALU:
            plantas_abiertas += f"  {j}: {int(pulp.value(w[j]))}\n"

        salida_flujo_bauxita = "\nFlujo de bauxita (X_ij):\n"
        for i,j in x:
            if pulp.value(x[(i,j)]) > 0:
                salida_flujo_bauxita +=  f"  {i}->{j}: {pulp.value(x[(i,j)]):,.2f}\n"
        
        salida_flujo_alumina = "\nFlujo de alumina (Y_jk):\n"
        for j,k in y:
            if pulp.value(y[(j,k)]) > 0:
                salida_flujo_alumina += f"  {j}->{k}: {pulp.value(y[(j,k)]):,.2f}\n"

        salida_flask = salida_costo + plantas_abiertas + salida_flujo_bauxita + salida_flujo_alumina

    return render_template("home2.html", salida_flask=salida_flask)


if __name__== "__main__":
    app.run(debug=True)