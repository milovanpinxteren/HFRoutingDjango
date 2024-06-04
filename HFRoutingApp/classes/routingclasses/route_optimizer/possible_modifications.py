# def selection(self): #Based on Routlette wheel with probability proportional to fitness
#     fitness_values = [self.fitness(chromosome) for chromosome in self.population]
#     total_fitness = sum(fitness_values)
#     probabilities = [fitness / total_fitness for fitness in fitness_values]
#     selected_parents = random.choices(self.population, weights=probabilities, k=self.population_size // 2)
#     return selected_parents


# def crossover(self, parent1, parent2):  # With midpoint crossover
#     child = {}
#     for vehicle in parent1:
#         midpoint = len(parent1[vehicle]) // 2
#         child[vehicle] = parent1[vehicle][:midpoint] + [gene for gene in parent2[vehicle] if
#                                                         gene not in parent1[vehicle][:midpoint]]
#     return child

# def crossover(self, parent1, parent2):  # With uniform crossover
#     child = {}
#     for vehicle in parent1:
#         new_route = []
#         for gene1, gene2 in zip(parent1[vehicle], parent2[vehicle]):
#             if random.random() < 0.5:
#                 new_route.append(gene1)
#             else:
#                 new_route.append(gene2)
#         child[vehicle] = new_route
#     return child

# def crossover(self, parent1, parent2):
#     child = {}
#     for vehicle in parent1:
#         parent1_route = parent1[vehicle]
#         parent2_route = parent2[vehicle]
#         preserved = parent1_route[:2]
#         preserved.extend(parent1_route[-2:])  # Preserve first and last two locations from parent1
#         remaining = [gene for gene in parent2_route if gene not in preserved]  # Remaining locations from parent2
#         # Combine preserved and remaining locations to form the child route
#         child_route = preserved + remaining
#         child[vehicle] = child_route
#     return child
#

####My version
# def crossover(self, parent1, parent2):
#     child = {}
#     for vehicle in parent1:
#         preserved_locations_parent1 = np.array(parent1[vehicle][:2] + parent1[vehicle][-2:])
#         preserved_locations_parent2 = np.array(parent2[vehicle][:2] + parent2[vehicle][-2:])
#         are_equal = np.array_equal(np.sort(preserved_locations_parent1), np.sort(preserved_locations_parent2))
#         if are_equal: #Check if the parents still have the same start and end point for the operator
#             remaining_locations_parent1 = parent1[vehicle][2:-2]
#             remaining_locations_parent2 = parent2[vehicle][2:-2]
#             try:
#                 random_index = random.randint(1, len(remaining_locations_parent2))
#                 if 0 <= random_index <= len(remaining_locations_parent1):
#                     if remaining_locations_parent2[random_index-1] not in preserved_locations_parent1:
#                         remaining_locations_parent1[random_index-1] = remaining_locations_parent2[random_index-1]
#                         remaining_locations_parent2[random_index-1] = remaining_locations_parent1[random_index-1]
#                     else:
#                         print('Tried to switch a preserved location')
#             except ValueError:
#                 print('No locations remaining')
#             child_locations = parent1[vehicle][:2] + remaining_locations_parent1 + parent1[vehicle][-2:]
#         else: #If the parents do not have the same start and end, do not do crossover
#             child_locations = parent1[vehicle]
#         child[vehicle] = child_locations
#     return child


###GPT
# def crossover(self, parent1, parent2):
#     child = {}
#     for vehicle in parent1:
#         preserved_locations_parent1 = np.array(parent1[vehicle][:2] + parent1[vehicle][-2:])
#         preserved_locations_parent2 = np.array(parent2[vehicle][:2] + parent2[vehicle][-2:])
#         are_equal = np.array_equal(np.sort(preserved_locations_parent1), np.sort(preserved_locations_parent2))
#         if are_equal:
#             remaining_locations_parent1 = parent1[vehicle][2:-2]
#             remaining_locations_parent2 = parent2[vehicle][2:-2]
#             try:
#                 random_index = random.randint(0, len(remaining_locations_parent1) - 1)
#                 if remaining_locations_parent2[random_index] not in preserved_locations_parent1:
#                     remaining_locations_parent1[random_index], remaining_locations_parent2[random_index] = (
#                         remaining_locations_parent2[random_index], remaining_locations_parent1[random_index]
#                     )
#                 else:
#                     print('Tried to switch a preserved location')
#             except (ValueError, IndexError) as e:
#                 print('Error:', str(e))
#             child_locations = parent1[vehicle][:2] + remaining_locations_parent1 + parent1[vehicle][-2:]
#         else:
#             child_locations = parent1[vehicle]
#         child[vehicle] = child_locations
#     return child