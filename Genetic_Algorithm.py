import __future__
import random


class Chromosome(object):
  def __init__(self, num_genes, bits = ""):
    self.__genes = {
    '0000':'0',
    '0001':'1',
    '0010':'2',
    '0011':'3',
    '0100':'4',
    '0101':'5',
    '0110':'6',
    '0111':'7',
    '1000':'8',
    '1001':'9',
    '1010':'+',
    '1011':'-',
    '1100':'*',
    '1101':'/'
    }

    self.__num_genes = num_genes
    self.__bits = ""
    self.__fitness = 0.0
    self.__gene_expession = ""
    self.__result = 0.0

    if len(bits) > 0:
      self.__bits = bits
    else:
      for i in xrange(4*self.__num_genes):
        if random.random() > 0.5:
          self.__bits += '1'
        else:
          self.__bits += '0'

  def get_bits(self):
    return self.__bits

  def get_fitness(self):
    return self.__fitness

  def set_bits(self, sequence):
    self.__bits = sequence

  def set_fitness(self, fitness):
    self.__fitness = fitness

  def get_result(self):
    self.decode()
    return self.__result

  def get_expression(self):
    return self.__gene_expession

  def mutate(self, mutationRate):
    t = ''
    # Mutate a bit acording to mutation rate
    for c in xrange(len(self.__bits)):
      if random.random() <= mutationRate:
        if self.__bits[c] == '0': 
          t += '1'
        elif self.__bits[c] == '1': 
          t += '0'
      else:
        t += self.__bits[c]
    self.__bits = t

  def cross_over(self, chromosome, crossOverRate):
    # Cross over according to crossover rate
    if random.random() <= crossOverRate:
      o = chromosome.get_bits()
      # Select a random crossover point
      ptr = random.randrange(0, len(o))
      # Cross over binary expressions
      child_a = Chromosome(num_genes=self.__num_genes ,
                 bits=o[:ptr]+self.__bits[ptr:])
      child_b = Chromosome(num_genes=self.__num_genes ,
                 bits=self.__bits[:ptr]+o[ptr:])
      return child_a, child_b
    return self, chromosome

  def gene_to_exp(self, exp):
    try:
      return self.__genes[exp]
    except:
      return ""

  def decode(self):
    sym = '+-*/'
    num = '0123456789'
    s   = ''
    ans = ''
    tot = 0.0
    # Assemble string bitstream into numbers/operators
    for n in xrange(len(self.__bits)/4):
      s += self.gene_to_exp(self.__bits[(n*4):(n*4+4)])

    for c in xrange(len(s)):
      if len(ans)%2 == 0:
        if s[c] in num: 
          ans += s[c]
    # Otherwise, parse operators
      else:
        if s[c] in sym: ans += s[c]
    try:
      # Cull out any trailing operator genes
        if ans[-1] in sym: ans = ans[:-1]
      self.__gene_expession = ans
      # eval - floating point
      self.__result = eval(compile(self.__gene_expession, '<string>', 
              'eval', __future__.division.compiler_flag))
    except IndexError:
      self.__gene_expession = ""
      self.__result = 0.0
    except ZeroDivisionError:
      self.__result = 0.0
    return ans







def roulette_selection(population, crossOver):
  # roulette wheel 2 members out of the current population
  # Probability of selection is proportional to fitness.
  # Such that, Ps = fitnes/sum(all fitnesses) 
  wheel    = []
  parents  = []
  totalFitness = 0.0
  # sum current population fitnesses
  for c in population: totalFitness += c.get_fitness()
  # construct the roulette wheel of probabilities
  for c in population: 
    try:
      wheel.append(c.get_fitness()/totalFitness)
    except ZeroDivisionError:
      wheel.append(0.0)
  while len(parents) < 2:
    spin_pos = random.random() / totalFitness
    for n in xrange(len(wheel)-1):
      if wheel[n] > spin_pos and wheel[n+1] < spin_pos:
        parents.append(population[n]) 
      else:
        parents.append(population[-1])
  return parents[0].cross_over(parents[1], crossOver)

def genetic_compute(targetValue, numGenes, populationSize, 
                    crossOverRate, mutationRate, maxGenerations):
  generations = 1
  max_fitness = 0.0
  # Generate a seed population and assign a fitness score (1/tgt-res)
  population = []
  for n in xrange(populationSize):
    c = Chromosome(num_genes = numGenes)
    try:
      # fitness approaches inf as result aproaches target
      fitness = 1.0/(targetValue - c.get_result())
      if fitness > max_fitness: 
        max_fitness = fitness
        print 'Generation - ', generations
        print 'Max fitness so far [', c.get_expression(), \
              '=', c.get_result(), '] Fitness = ', fitness, '\n'
    except ZeroDivisionError:
      print 'Solution found! {0} = {1}'.format(c.get_expression(), targetValue)
      return True
    c.set_fitness(fitness)
    population.append(c)  

  while generations < maxGenerations:
    generations += 1
    new_population  = []
    while len(new_population) < populationSize:
      # Roulette out a new population of children
      children = roulette_selection(population, crossOverRate)
      # mutate accordingly
      for child in children: 
        child.mutate(mutationRate)
        new_population.append(child)
        try:
          # fitness approaches inf as result aproaches target
          fitness = 1.0/(targetValue - child.get_result())
          child.set_fitness(fitness)
          if fitness > max_fitness: 
            max_fitness = fitness
            print 'Generation - ', generations
            print 'Max fitness so far [', child.get_expression(), \
                  '=', child.get_result(), '] Fitness = ', fitness, '\n'
        except ZeroDivisionError:
          print 'Solution found! {0} = {1}'.format(child.get_expression(), targetValue)
          return True
    population = new_population


if __name__ == '__main__':
  # no parentheses, prime/prime is unlikely to be completely calculated!
  # 17/19 != 9+8/9+9+1, as opposed to (9+8)/(9+9+1)
  # used to tune time vs. exploration vs. convergence
  genetic_compute(targetValue   = (13.5), 
                  numGenes      = 40, 
                  populationSize= 100, 
                  crossOverRate = 0.7, 
                  mutationRate  = 0.01, 
                  maxGenerations= 200000)