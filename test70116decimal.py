#decimal
import decimal
import sys
decimal.getcontext().prec=2
print decimal.Decimal('1')/decimal.Decimal('3')
sys.exit()
print 1/.3
