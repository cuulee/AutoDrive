import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.Q = {}
        self.policy = {}
        self.alpha = 0.4
        self.gamma = 0.3
        self.actions = [None, 'forward', 'right', 'left']

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)
        # The states can be defined as what the current environment is, .i.e., the traffic light and the intersection situation +
        # the location of the next waypoint.(Hardcoding states is kind of bad idea as they are many of them)
        self.state = inputs
        self.state['next_waypoint'] = self.next_waypoint
        self.state = tuple(self.state.items())
        # select random action if state not present in the policy: Agent has not seen the state

        # TODO: Select action according to your policy
        #print type(self.policy)
        action = self.actions[random.randrange(4)] if self.state not in self.policy else self.policy[self.state]
        reward = self.env.act(self, action)
        state_prime = self.env.sense(self)
        state_prime['next_waypoint'] = self.planner.next_waypoint()
        state_prime = tuple(state_prime.items())
        
        # Now we have all the variables that are input to q learning formula: state, reward, action, and next_state:
        # What goes next? We tweak q_value for the present state action pair and then choose the action of the state which maximized q(the optimal policy)
        # According to the formula we need to calculate the utility of the next state. max(a) Q(s', a'). The policy is holding argmax(a) Q(s,a) values.
        # Thus, as the Q learning algorithm converges, we would be finding he max(a) Q(s', a') if the policy has seen that state. Thus, there is no need to
        # calculate the max(a') Q(s', a') everytime as that would be recursively going on till i don't know what
        
        action_prime  = self.actions[random.randrange(4)] if state_prime not in self.policy else self.policy[state_prime]

        # TODO: Learn policy based on state, action, reward
        # Q_learning
        state_act_pair = (self.state, action)
        self.Q[state_act_pair] = (1 - self.alpha) * self.Q.get(state_act_pair, 0) + self.alpha*(reward + self.gamma*(self.Q.get((state_prime, action_prime), 0)))
        # Now we need to update the policy well(Take action that maximizes the utility of the present state, thus updating policy)
        Q_max_candidates = [self.Q.get((self.state, act)) for act in self.actions]
        try:
            if None not in Q_max_candidates:
                # PERFORMS VERY POORLY WHEN ALL STATES NOT ALREADY SEEN.(11/100) THIS IS SO BECAUSE THE POLICY SHOULD NOT BE UPDATED 
                # UNTIL ALL THE ACTIONS CORRESPONDING TO THE STATE HAS BEEN SEEN. OR ELSE IT WILL KEEP FOLLOWING THE SAME POLICY. AND 
                # WILL NEVER FURTHER LEARN.
                # ANOTHER METHOD IS THE EXPLORATION-EXPLOITATION METHOD WHEREBY THE ACTION IN THE POLICY IS TAKEN WITH PROB 1-e AND ANOTHER
                # RANDOM ACTION WITH PROB e. 
                Q_max = max(Q_max_candidates)
                actions_candidates = [act for act in self.actions if Q_max == self.Q.get((self.state, act))]
                self.policy[self.state]= random.choice(actions_candidates)
        except Exception as e:
            print "Could not update the policy by choosing the max Q: {}".format(e)
        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.5, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
