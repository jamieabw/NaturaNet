# Predator-Prey Evolution Simulator

**Work in Progress!**

This project is a Python-based simulation using Pygame and a simple neural network architecture to evolve prey agents over generations via natural selection.

The prey agents learn to navigate a 2D environment to seek out food, avoid predators, and gradually develop more effective movement strategies.

---

## Features

- Agents ("prey") use a basic neural network to decide movement directions.
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

## Missing / Planned Features

- Terrain generation and varied obstacles (planned).
- Reinforcement learning (may be explored in future versions).

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

---

## Demonstration

[Link here](https://youtu.be/TuRSZjvvx5c)

Above is an example of natural selection over 130 generations with this project (does not use sprites or include predators as old version used)

---

## Bugs & Development

This is an active and experimental project:

- Bugs and unexpected behaviors are expected.
- Features, algorithms, and parameters are likely to change as development continues.
- Feedback and suggestions are always welcome.

---

## Requirements

- Python 3.x
- Pygame
- NumPy

---

## Future directions

- Implement terrain and environment variation.
- Possibly integrate reinforcement learning to allow agents to learn from explicit rewards on a per-move basis.


