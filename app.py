import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Cargar el archivo Excel
ruta_excel = r"F:\Users\sfarias\Documents\Curso Python\.vscode\Reportes_Comunales\Salidas\Excel\Brechas_Ingresos_Region_2_transpuesto.xlsx"
df = pd.read_excel(ruta_excel)

# Filtrar comunas válidas
comunas_validas = ~df['Nombre_comuna'].str.startswith(('Region de', 'Provincia de', 'Regional', 'Nacional'))
df = df[comunas_validas].copy()

# Calcular brechas para 2018 y 2022
df['Brecha_2018'] = df['Masculino_YEAR_2018'] - df['Femenino_YEAR_2018']
df['Brecha_2022'] = df['Masculino_YEAR_2022'] - df['Femenino_YEAR_2022']

# Pivoteo para la tabla comparativa
tabla_brechas = df[['Nombre_comuna', 'Brecha_2018', 'Brecha_2022']].set_index('Nombre_comuna')

# Mostrar tabla en consola
print(tabla_brechas)

# Crear gráfico de comparación
plt.figure(figsize=(14, 6))
tabla_brechas.sort_values('Brecha_2022', ascending=False, inplace=True)
tabla_brechas.plot(kind='bar', width=0.75)

plt.title('Comparación de Brechas de Ingreso por Comuna (2018 vs 2022)', fontsize=14)
plt.ylabel('Brecha de Ingreso (Masculino - Femenino)')
plt.xlabel('Comuna')
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.legend(title='Año')

# Guardar o mostrar gráfico
plt.savefig('comparacion_brechas_por_comuna.png', dpi=300)
plt.show()
