# def selection(self): #Based on Routlette wheel with probability proportional to fitness
#     fitness_values = [self.fitness(chromosome) for chromosome in self.population]
#     total_fitness = sum(fitness_values)
#     probabilities = [fitness / total_fitness for fitness in fitness_values]
#     selected_parents = random.choices(self.population, weights=probabilities, k=self.population_size // 2)
#     return selected_parents

# def fitness(self, chromosome):
#     try:
#         total_distance = 0
#         for vehicle, route in chromosome.items():
#             total_load = 0
#             route_distance = 0
#             for i in range(len(route)):
#                 if i < len(route) - 1:
#                     try:
#                         spot_id = self.location_to_spot[route[i]]
#                         total_load += self.spot_crates[spot_id]
#                     except KeyError:  # spot not found -> error or it is a driver
#                         total_load += 0
#                     route_distance += self.distance_matrix[(route[i], route[i + 1])]
#             total_distance += route_distance
#         return total_distance
#     except Exception as e:
#         print(e)
#         return float("-inf")

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


# def crossover(self, parent1, parent2):
#     try:
#         child = parent1.copy() #Copy parent, will be the child
#         vehicle = random.choice(list(parent1.keys())) #Get a random route from parent1
#         remaining_locations_parent1 = parent1[vehicle][2:-2] #Get the (non-preserved) locations of route
#         child_locations_to_insert = remaining_locations_parent1.copy()
#         random_parent1_index = random.randint(1, len(remaining_locations_parent1) - 1) #Get a random index
#         old_value = remaining_locations_parent1[random_parent1_index] #The value of the random stop
#
#         remaining_locations_parent2 = parent2[random.choice(list(parent2.keys()))][2:-2] #Get random loc from par2
#         random_parent2_index = random.randint(1, len(remaining_locations_parent2) - 1) #Get index
#         new_value = remaining_locations_parent2[random_parent2_index] #New random value
#         print('OLD', vehicle, 'locs:', remaining_locations_parent1)
#         if new_value not in child_locations_to_insert:
#             child_locations_to_insert[random_parent1_index] = new_value #Replace old value with new
#             for key, value_list in child.items():  # Replace occurence of new value in child with old
#                 if new_value in value_list:
#                     value_list[value_list.index(new_value)] = old_value
#                     print('NEW', vehicle, 'locs:', child_locations_to_insert)
#                     child_locations = child[vehicle][:2] + child_locations_to_insert + child[vehicle][-2:]
#                     child[vehicle] = child_locations
#                     if child:
#                         return child
#                     else:
#                         print('Child', child)
#         else:
#             print('ALREADY IN ROUTE')
#             return parent1
#     except Exception as e:
#         print(e)
#         return parent1






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