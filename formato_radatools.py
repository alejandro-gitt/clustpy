import pandas as pd

nodes_path = r'C:\Users\proal\Documents\UC3M\2021-2022\2\TFG\codigo\Nodes_t1.csv'
edges_nohead_path = r'C:\Users\proal\Documents\UC3M\2021-2022\2\TFG\codigo\Edges_t1_no_header.csv'

edges_path = r'C:\Users\proal\Documents\UC3M\2021-2022\2\TFG\algoritmo1\datos\Edges_t1_noneg.csv'
df_nodes = pd.read_csv(nodes_path, sep = ';',encoding='unicode_escape')
df_edges_nohead= pd.read_csv(edges_nohead_path, sep = ';',encoding='unicode_escape',usecols=[0,1,2])
df_edges = pd.read_csv(edges_path, sep = ';',encoding='unicode_escape')

'''Para la red entera:'''
# print(df_edges)
# f = open("edges_for_rada-full.txt", "a")
# f.write(df_edges.to_string(index = False))
# f.close()

'''Clase por clase'''
string_curso = '3º ESO'
string_grupo = 'B'
# string_clase = '2º ESO A' #Unused 
# Eliminamos los enlaces fuera de la clase
alumnos_en_aula = df_nodes[df_nodes["Curso"] == string_curso][df_nodes["Grupo"] == string_grupo]['Nodes']
print(list(alumnos_en_aula))
fromtos = []
for alumno in alumnos_en_aula:
    fromtos.append(list(zip(list(df_edges.loc[df_edges['from'] == alumno]['from']),list(df_edges.loc[df_edges['from'] == alumno]['to']),list(df_edges.loc[df_edges['from'] == alumno]['weight']))))
enlaces_aula = [item for sublist in fromtos for item in sublist]

enlaces_aula_filtrado = [(u,v,w) for (u,v,w) in enlaces_aula if v in list(alumnos_en_aula)] #Guardamos solo los enlaces que apunten dentro de la clase

listToStr = ' '.join([str(elem) for elem in enlaces_aula_filtrado])
# x = listToStr.replace(") (", "\n").replace("(","").replace(")","").replace(",","")
x = listToStr.replace(") (","),(")
# print(column_list)
f = open("edges_tercero_B_noneg.txt", "a")
f.write(x)
f.close()