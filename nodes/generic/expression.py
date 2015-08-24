import bpy
import ast
from bpy.props import *
from ... sockets.info import toIdName
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

variableNames = list("xyzabcdefghijklmnopqrstuvw")

class ExpressionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ExpressionNode"
    bl_label = "Expression"

    def settingChanged(self, context = None):
        self.executionError = ""
        self.containsSyntaxError = not isExpressionValid(self.expression)
        executionCodeChanged()

    expression = StringProperty(name = "Expression", update = settingChanged)
    containsSyntaxError = BoolProperty()
    executionError = StringProperty()

    def create(self):
        self.width = 200
        socket = self.inputs.new("an_NodeControlSocket", "New Input")
        socket.drawCallback = "drawNewInputSocket"
        self.outputs.new("an_GenericSocket", "Result", "result")

    def draw(self, layout):
        layout.prop(self, "expression", text = "")
        if self.containsSyntaxError:
            layout.label("Syntax Error", icon = "ERROR")
        if self.executionError != "":
            layout.label(self.executionError, icon = "ERROR")

    def drawNewInputSocket(self, layout):
        row = layout.row()
        row.alignment = "LEFT"
        self.functionOperator(row, "chooseNewInputType", text = "New Input", emboss = False)

    def chooseNewInputType(self):
        self.chooseSocketDataType("newInputSocket")

    @property
    def inputNames(self):
        return {socket.identifier : socket.customName for socket in self.inputs}

    def getExecutionCode(self):
        expression = self.expression.strip()
        if expression == "" or self.containsSyntaxError: return "result = None"

        lines = []
        lines.append("try: result = " + expression)
        lines.append("except:")
        lines.append("    result = None")
        lines.append("    self.executionError = str(sys.exc_info()[1])")
        return lines

    def getModuleList(self):
        return ["sys"]

    def edit(self):
        emptySocket = self.inputs["New Input"]
        directOrigin = emptySocket.directOriginSocket
        if directOrigin is None: return
        dataOrigin = emptySocket.dataOriginSocket
        if dataOrigin.dataType == "Node Control": return
        socket = self.newInputSocket(dataOrigin.dataType)
        emptySocket.removeConnectedLinks()
        socket.linkWith(directOrigin)

    def newInputSocket(self, dataType):
        name = self.getNewSocketName()
        socket = self.inputs.new(toIdName(dataType), name, "input")
        socket.dataIsModified = True
        socket.nameSettings.editable = True
        socket.nameSettings.variable = True
        socket.nameSettings.unique = True
        socket.displayCustomName = True
        socket.display.customNameInput = True
        socket.customName = name
        socket.moveable = True
        socket.removeable = True
        socket.moveUp()
        if len(self.inputs) > 2:
            socket.copyDisplaySettingsFrom(self.inputs[0])
        return socket

    def getNewSocketName(self):
        inputs = self.inputsByCustomName
        for name in variableNames:
            if name not in inputs: return name
        return "x"

    def socketChanged(self):
        self.settingChanged()
        executionCodeChanged()

def isExpressionValid(expression):
    try:
        ast.parse(expression)
        return True
    except SyntaxError:
        return False