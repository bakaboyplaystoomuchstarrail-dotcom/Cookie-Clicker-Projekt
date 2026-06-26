class Action():
    def __init__(self,_Action):
        self.Action = _Action
    
    def AssignProperties(self,):
        self.Tie = self.Action
        if self.Action == "Rock":
            self.Strength = "Scissors"
            self.Weakness = "Paper"
        elif self.Action == "Paper":
            self.Strength = "Rock"
            self.Weakness = "Scissors"
        elif self.Action == "Scissors":
            self.Strength = "Paper"
            self.Weakness = "Rock"

Actions = [Action("Rock"),Action("Paper"),Action("Scissor")]
for x in range(len(Actions)):
    Actions[x].AssignProperties()

class Input_Neuron():
    def __init__(self,_Action):
        self.Action = _Action

class Neuron():
    def __init__(self,_Weights):
        self.Action = None
        self.Weights = _Weights

class Weight():
    def __init__(self,_OriginNeuron,_TerminalNeuron=None):
        self.OriginNeuron = _OriginNeuron
        self.TerminalNeuron = _TerminalNeuron

class Layer():
    def __init__(self,_Neurons):
        self.Neurons = _Neurons

class NeuralNetwork():
    def __init__(self,_Layers=None):
        self.Layers = _Layers

FAH = NeuralNetwork([Layer([])])

#START
Ans = "play"
Turns = 0
while Ans != "end":
    UserAction = input("What do you want to play? Type 0 for Rock, 1 for Paper, 2 for Scissors and 'end' to exit")
    if UserAction == "end":
        break
    UserAction = Actions[UserAction]

    Layers = FAH.Layers
    for Layer in Layers:
        Neurons = Layers[Layer].Neurons
        for Neuron in Neurons:
            Weights = Neurons[Neuron].Weights


    CorrectResponse = UserAction.Weakness
    Tie = UserAction.Tie
    BadResponse = UserAction.Strength

