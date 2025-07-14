# Predator-Prey Evolution Simulator


This project is a Python-based simulation using Pygame and a simple neural network architecture to evolve prey agents over generations via natural selection.

The prey agents learn to navigate a 2D environment to seek out food, avoid predators, and gradually develop more effective movement strategies.

---

## Features

- Agents use a basic neural network to decide movement directions.
- Evolution is driven by natural selection:
  - The most successful prey and predators (based on a custom fitness factor) reproduce to form the next generation.
  - Genetic crossover and mutation are used to evolve weights and biases.
- Agents can mutate to explore new behaviors.
- Wall collisions penalize fitness, encouraging smarter exploration.
- Agents currently receive rewards for:
  - Moving closer to food.
  - Discovering and consuming food.
  - Staying alive.

---

## Potential future features

- Terrain generation and varied obstacles.
- Reinforcement learning.

---

## How it works

- Each agent's "intelligence" is a small neural network with inputs such as:
  - Distance and direction to food.
  - Distance and direction to predator.
  - Distances to walls.
  - Previous movement decisions.
- A generation runs until all agents die or time runs out.
- Top-performing agents are selected to produce the next generation through genetic crossover and mutation.
- Over time, agents improve their ability to find and consume food.
- At any time, press space to view the statistics of the learning process.
- Predators introduced from generation 200 onwards to give prey a headstart.

---

## Bugs & Development

This is an active and experimental project:

- Bugs and unexpected behaviors are expected.
- Features, algorithms, and parameters are likely to change as development continues.
- Feedback and suggestions are always welcome.

---

## Video Examples
1) (Generations 1-200) https://youtu.be/IMZjztsO-gs
2) (Generations 200-525) https://youtu.be/372iaDMlbvQ

---

## Requirements

- Python 3.x
- Pygame
- NumPy

