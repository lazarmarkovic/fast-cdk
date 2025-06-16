MM = """
VPCDef: 'VPC' statements*=AssignmentStatement;
AssignmentStatement: var=ID '=' value=Value;
Value: INT;
"""
