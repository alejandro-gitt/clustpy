# clustpy
This is a python implementation of communities detection in complex networks using tabu modularity optimization.

It uses Networkx's networks class for being able to use all of theirs functions https://networkx.org/documentation/stable/reference/index.html

In this repo you'll find:

- *mymod.py*: Contains a function (mymodularity) that computes a network's modularity. This is an extension of networkx's to also compute modularity on directed, positively or negatively weighted graphs.
- calc_mod_example.py: Example for mymodularity's use. Script with a hard-coded example multidigraph with the only purpose of calculating its modularity.

- *tabusearch.py*: Contains the tabu_modularity_optimization function, that will execute the tabu communities search for the input network.
Please note that this algorithm works best when executed a number of iterations such that the output of the previous iteration will be the input for the current iteration and so on. An example of this is shown at the funcion n_times_tabu that may be found in the testing.py file.

- *testing.py*: Contains an in-depth example. Here we create graphs for different classrooms in a school, compute modularity, apply tabu and draw the different communities found.

Example:
After applying 10 times tabu we can find that, according to its edges and modularity, the next graph has a final modularity of more than 0.28:


![image](https://user-images.githubusercontent.com/61252229/166304151-153453e4-69c4-476a-a6b9-4c1e376dfd71.png)
