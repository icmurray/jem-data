'''
Register configuration tables for Dirus products
'''

TABLE_1 = dict( (addr,2) for addr in range(0xC550, 0xC58C + 1, 2) )
TABLE_2 = dict( (addr,2) for addr in range(0xC650, 0xC681 + 1, 2) )

TABLE_3 = dict( (addr,2) for addr in range(0xC750, 0xC78E + 1, 2) )
TABLE_3.update( dict( (addr,1) for addr in range(0xC790, 0xC795 + 1, 1) ))

TABLE_4 = dict( (addr,1) for addr in range(0xC850, 0xC871 + 1, 1) )
TABLE_5 = dict( (addr,1) for addr in range(0xC900, 0xC907 + 1, 1) )
TABLE_6 = dict( (addr,1) for addr in range(0xC950, 0xCA92 + 1, 1) )

TABLES = [TABLE_1, TABLE_2, TABLE_3, TABLE_4, TABLE_5, TABLE_6]

ALL = {}
for t in TABLES:
    ALL.update(t)
