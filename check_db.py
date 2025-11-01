import sqlite3

conn = sqlite3.connect('data/data.db')
cursor = conn.cursor()

# Ver estructura de tabla
cursor.execute('PRAGMA table_info(measurements)')
print('📋 Estructura de la tabla measurements:')
for col in cursor.fetchall():
    print(f'  • {col[1]} ({col[2]})')

# Contar registros
cursor.execute('SELECT COUNT(*) FROM measurements')
total = cursor.fetchone()[0]
print(f'\n✅ Total de registros en BD: {total}')

# Ver primeros 3 registros
cursor.execute('SELECT * FROM measurements LIMIT 3')
print('\n📊 Primeros 3 registros:')
for row in cursor.fetchall():
    print(f'  ID: {row[0]} | client: {row[1]} | te: {row[2]:.1f}°C | hr: {row[3]:.1f}%')

# Ver estadísticas
cursor.execute('SELECT AVG(te), AVG(hr), AVG(mp01), AVG(mp25), AVG(mp10) FROM measurements')
stats = cursor.fetchone()
print(f'\n📈 Estadísticas generales:')
print(f'  • Temperatura promedio: {stats[0]:.1f}°C')
print(f'  • Humedad promedio: {stats[1]:.1f}%')
print(f'  • MP01 promedio: {stats[2]:.1f} ug/m³')
print(f'  • MP25 promedio: {stats[3]:.1f} ug/m³')
print(f'  • MP10 promedio: {stats[4]:.1f} ug/m³')

conn.close()
