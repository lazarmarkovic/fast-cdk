MM = """
VPCDef: 'VPC' statements*=AssignmentStatement;
AssignmentStatement: var=ID '=' value=Value;
Value: INT;
"""

M2 = """
VPCDef: 'VPC' statements*=AssignmentStatement;
AssignmentStatement: var=ID '=' value=Value;
Value: INT | STRING;
STRING: '"' value=ID '"';
"""
