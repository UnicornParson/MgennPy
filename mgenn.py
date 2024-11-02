ym_for_each_insn'
  - 'sym_for_each_insn_continue_reverse'
  - 'symbols__for_each_entry'
  - 'tb_property_for_each'
  - 'tcf_act_for_each_action'
  - 'tcf_exts_for_each_action'
  - 'ttm_resource_manager_for_each_res'
  - 'udp_portaddr_for_each_entry'
  - 'udp_portaddr_for_each_entry_rcu'
  - 'usb_hub_for_each_child'
  - 'v4l2_device_for_each_subdev'
  - 'v4l2_m2m_for_each_dst_buf'
  - 'v4l2_m2m_for_each_dst_buf_safe'
  - 'v4l2_m2m_for_each_src_buf'
  - 'v4l2_m2m_for_each_src_buf_safe'
  - 'virtio_device_for_each_vq'
  - 'while_for_each_ftrace_op'
  - 'xa_for_each'
  - 'xa_for_each_marked'
  - 'xa_for_each_range'
  - 'xa_for_each_start'
  - 'xas_for_each'
  - 'xas_for_each_conflict'
  - 'xas_for_each_marked'
  - 'xbc_array_for_each_value'
  - 'xbc_for_each_key_value'
  - 'xbc_node_for_each_array_value'
  - 'xbc_node_for_each_child'
  - 'xbc_node_for_each_key_value'
  - 'xbc_node_for_each_subkey'
  - 'ynl_attr_for_each'
  - 'ynl_attr_for_each_nested'
  - 'ynl_attr_for_each_payload'
  - 'zorro_for_each_dev'

IncludeBlocks: Preserve
IncludeCategories:
  - Regex: '.*'
    Priority: 1
IncludeIsMainRegex: '(Test)?$'
IndentCaseLabels: false
IndentGotoLabels: false
IndentPPDirectives: None
IndentWidth: 8
IndentWrappedFunctionNames: false
JavaScriptQuotes: Leave
JavaScriptWrapImports: true
KeepEmptyLinesAtTheStartOfBlocks: false
MacroBlockBegin: ''
MacroBlockEnd: ''
MaxEmptyLinesToKeep: 1
NamespaceIndentation: None
ObjCBinPackProtocolList: Auto
ObjCBlockIndentWidth: 8
ObjCSpaceAfterProperty: true
ObjCSpaceBeforeProtocolList: true

# Taken from git's rules
PenaltyBreakAssignment: 10
PenaltyBreakBeforeFirstCallParameter: 30
PenaltyBreakComment: 10
PenaltyBreakFirstLessLess: 0
PenaltyBreakString: 10
PenaltyExcessCharacter: 100
PenaltyReturnTypeOnItsOwnLine: 60

PointerAlignment: Right
ReflowComments: false
SortIncludes: false
SortUsingDeclarations: false
SpaceAfterCStyleCast: false
SpaceAfterTemplateKeyword: true
SpaceBeforeAssignmentOperators: true
SpaceBeforeCtorInitializerColon: true
SpaceBeforeInheritanceColon: true
SpaceBeforeParens: ControlStatementsExceptForEachMacros
SpaceBeforeRangeBasedForLoopColon: true
SpaceInEmptyParentheses: false
SpacesBeforeTrailingComments: 1
SpacesIn