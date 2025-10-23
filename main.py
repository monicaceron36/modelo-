from flask import Flask, render_template, request


app = Flask(__name__)  


@app.route("/", methods=["GET", "POST"])  # con el metodo get lo que hace es que me toma la informacion del formulario me coge los valores del cuadro y lo trae a python al termnal del modelo
def home():
    costo_total=0
    if request.method=="POST":
        Costo_1=request.form.get("costo_1")    # GET ES  PARA RECIBIR Y POST PARA ENVIAR los dato del html para un espacio 
        print("dato_1", Costo_1)
        costo_2=request.form.get("costo_2")
        print("dato_2", costo_2)

        costo_total= int(Costo_1) + int(costo_2)

    return render_template ("home.html", costo_total=costo_total)

    



if __name__=="__main__":
    app.run(debug=True)