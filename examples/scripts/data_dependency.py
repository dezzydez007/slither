import sys
from slither import Slither
from slither.analyses.data_dependency.data_dependency import is_dependent, is_tainted, pprint_dependency
from slither.core.declarations.solidity_variables import SolidityVariableComposed
from slither.slithir.variables import Constant

if len(sys.argv) != 2:
    print('Usage: python data_dependency.py file.sol')
    exit(-1)

slither = Slither(sys.argv[1])

contract = slither.get_contract_from_name('Simple')

destination = contract.get_state_variable_from_name('destination')
source = contract.get_state_variable_from_name('source')

print('{} is dependent of {}: {}'.format(source, destination, is_dependent(source, destination, contract)))
assert not is_dependent(source, destination, contract)
print('{} is dependent of {}: {}'.format(destination, source, is_dependent(destination, source, contract)))
assert is_dependent(destination, source, contract)
print('{} is tainted {}'.format(source, is_tainted(source, contract)))
assert not is_tainted(source, contract)
print('{} is tainted {}'.format(destination, is_tainted(destination, contract)))
assert is_tainted(destination, contract)

contract = slither.get_contract_from_name('Reference')

destination = contract.get_state_variable_from_name('destination')
destination_val = (destination, Constant('val'))
source = contract.get_state_variable_from_name('source')
source_val = (source, Constant('val'))

print()
print('Reference contract')
print('{}.val is dependent of {}: {}'.format(source, destination, is_dependent(source, destination_val, contract)))
assert not is_dependent(source, destination, contract)
print('{}.val is dependent of {}: {}'.format(destination, source, is_dependent(destination_val, source_val, contract)))
assert is_dependent(destination_val, source_val, contract)
print('{}.val is tainted {}'.format(source, is_tainted(source_val, contract)))
assert not is_tainted(source, contract)
print('{}.val is tainted {}'.format(destination, is_tainted(destination_val, contract)))
assert is_tainted(destination_val, contract)

destination_indirect_1 = contract.get_state_variable_from_name('destination_indirect_1')
destination_indirect_1_val = (destination_indirect_1, Constant('val'))

print('{} is tainted {}'.format(destination_indirect_1, is_tainted(destination_indirect_1_val, contract)))
assert is_tainted(destination_indirect_1_val, contract)

destination_indirect_2 = contract.get_state_variable_from_name('destination_indirect_2')
destination_indirect_2_val = (destination_indirect_2, Constant('val'))

print('{} is tainted {}'.format(destination_indirect_2, is_tainted(destination_indirect_2_val, contract)))
assert is_tainted(destination_indirect_2_val, contract)

print()
print('SolidityVar contract')

contract = slither.get_contract_from_name('SolidityVar')

addr_1 = contract.get_state_variable_from_name('addr_1')
addr_2 = contract.get_state_variable_from_name('addr_2')
msgsender = SolidityVariableComposed('msg.sender')
print('{} is dependent of {}: {}'.format(addr_1, msgsender, is_dependent(addr_1, msgsender, contract)))
assert is_dependent(addr_1, msgsender, contract)
print('{} is dependent of {}: {}'.format(addr_2, msgsender, is_dependent(addr_2, msgsender, contract)))
assert not is_dependent(addr_2, msgsender, contract)

print()
print('Intermediate contract')
contract = slither.get_contract_from_name('Intermediate')
destination = contract.get_state_variable_from_name('destination')
source = contract.get_state_variable_from_name('source')

print('{} is dependent of {}: {}'.format(destination, source, is_dependent(destination, source, contract)))
assert is_dependent(destination, source, contract)

print()
print('Base Derived contract')
contract = slither.get_contract_from_name('Base')
contract_derived = slither.get_contract_from_name('Derived')
destination = contract.get_state_variable_from_name('destination')
source = contract.get_state_variable_from_name('source')

print('{} is dependent of {}: {} (base)'.format(destination, source, is_dependent(destination, source, contract)))
assert not is_dependent(destination, source, contract)
print('{} is dependent of {}: {} (derived)'.format(destination, source, is_dependent(destination, source, contract_derived)))
assert is_dependent(destination, source, contract_derived)

print()
print('PropagateThroughArguments contract')
contract = slither.get_contract_from_name('PropagateThroughArguments')
var_tainted = contract.get_state_variable_from_name('var_tainted')
var_not_tainted = contract.get_state_variable_from_name('var_not_tainted')
var_dependant = contract.get_state_variable_from_name('var_dependant')

f = contract.get_function_from_signature('f(uint256)')
user_input = f.parameters[0]
f2 = contract.get_function_from_signature('f2(uint256,uint256)')

print('{} is dependent of {}: {} (base)'.format(var_dependant, user_input, is_dependent(var_dependant, user_input, contract)))
assert is_dependent(var_dependant, user_input, contract)
print('{} is tainted: {}'.format(var_tainted, is_tainted(var_tainted, contract)))
assert is_tainted(var_tainted, contract)
print('{} is tainted: {}'.format(var_not_tainted, is_tainted(var_not_tainted, contract)))
assert not is_tainted(var_not_tainted, contract)


print()
print('Nested')

contract = slither.get_contract_from_name('Nested')
n = contract.get_state_variable_from_name('n')
n_l_st_val1 = (n, Constant('l'), Constant('st'), Constant('val1'))
n_m_st_val2 = (n, Constant('m'), Constant('st'), Constant('val2'))
state_b = contract.get_state_variable_from_name('state_b')

txt = f'{".".join([str(x) for x in n_l_st_val1])} is dependent of {".".join([str(x) for x in n_m_st_val2])}:'
txt += f' {is_dependent(n_l_st_val1, n_m_st_val2, contract)}'
print(txt)
assert not is_dependent(n_l_st_val1, n_m_st_val2, contract)

txt = f'{".".join([str(x) for x in n_m_st_val2])} is dependent of {".".join([str(x) for x in n_l_st_val1])}:'
txt += f' {is_dependent(n_m_st_val2, n_l_st_val1, contract)}'
print(txt)
assert is_dependent(n_m_st_val2, n_l_st_val1, contract)
