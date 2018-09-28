from http.server import HTTPServer, BaseHTTPRequestHandler
import sqlite3
from urllib.parse import urlparse, parse_qs
import json



def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    server_address = ('http://julienlabonte.ca/', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        req = urlparse(self.path)
        query = parse_qs(req.query)

        conn = sqlite3.connect('bieres.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        self.send_response(200)

        self.send_header("content-type", "application/json")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if 'id' in query:
            c.execute("SELECT rowid, * FROM biere WHERE rowid=?", query['id'])
            bieres = c.fetchall()
        else:
            c.execute("SELECT rowid, * FROM biere")  # sqlite a un build in id. Le rajoute aussi pour des besoins futures d'affichage
            bieres = c.fetchall()  # Recupere les donnees de la base de donne

        res = [dict(biere) for biere in bieres]

        self.wfile.write(json.dumps(res).encode("UTF-8"))

        conn.commit()

        conn.close()


    def do_POST(self):
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)

        conn = sqlite3.connect('bieres.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        req = urlparse(self.path)


        if req.path == '/create':
            reqDecode = post_body.decode("UTF-8")
            reqParse = parse_qs(reqDecode)
            #Le strip vient enlever les caracteres superflus et le float vient tranformer le pourcentage en chiffre.
            #Besoin de faire des str parce que sinon il s'agit de listes.
            nom = reqParse['nom'][0]
            brasserie = reqParse['brasserie'][0]
            pourcentage = reqParse['pourcentage'][0]
            nBiere = (nom, brasserie, pourcentage)
            print(nBiere)
            c.execute("INSERT INTO biere VALUES (?,?,?)", nBiere)
            res = "La biere a ete cree"

            print(res)

            self.send_response(200)

            self.send_header("content-type", "application/json")
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            self.wfile.write(json.dumps(res).encode("UTF-8"))


        if req.path == '/delete':
            reqDecode = post_body.decode("UTF-8")
            reqParse = parse_qs(reqDecode)
            id = reqParse['id'][0]
            c.execute("DELETE FROM biere WHERE rowid = (?)", (id,))
            res = "La biere a ete supprime"

            self.send_response(200)

            self.send_header("content-type", "application/json")
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            self.wfile.write(json.dumps(res).encode("UTF-8"))


        if req.path == '/update':
            reqDecode = post_body.decode("UTF-8")
            reqParse = parse_qs(reqDecode)
            nom = reqParse['nom'][0]
            brasserie = reqParse['brasserie'][0]
            pourcentage = reqParse['pourcentage'][0]
            id = reqParse['id'][0]
            nBiere = (nom, brasserie, pourcentage, id)
            c.execute("UPDATE biere SET nom = ?, brasserie = ?, pourcentage = ? WHERE rowid = ?", nBiere)
            res = "La biere a ete modifie"

            print(res)

            self.send_response(200)

            self.send_header("content-type", "application/json")
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            self.wfile.write(json.dumps(res).encode("UTF-8"))

        conn.commit()

        conn.close()



run(handler_class=Handler)