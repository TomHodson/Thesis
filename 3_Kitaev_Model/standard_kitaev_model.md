---
title: The Kitaev Honeycomb Model
description: A short introduction to the weird and wonderful world of exactly solvable quantum models. This is an excerpt from my thesis.
image:
---

Here is a footnote reference,[^1] and another.[^longnote]

[^1]: Here is the footnote.

[^longnote]: Here's one with multiple blocks.

    Subsequent paragraphs are indented to show that they
belong to the previous footnote.

        { some.code }

    The whole paragraph can be indented, or just the first
    line.  In this way, multi-paragraph footnotes work like
    multi-paragraph list items.

This paragraph won't be part of the note, because it
isn't indented.

## The Kitaev Honeycomb Model

The Kitaev-Honeycomb model is remarkable because it was the first such model that combined three key properties.

First, it is a plausible tight binding Hamiltonian. The form of the Hamiltonian could be realised by a real material. Indeed candidate materials such as \ce{\alpha-RuCl3} were quickly found \cite{banerjeeProximateKitaevQuantum2016, trebstKitaevMaterials2022} that are expected to behave according to the Kitaev with small corrections. 

Second, the Kitaev Honeycomb model is deeply interesting to modern condensed matter theory. Its ground state is almost the canonical example of the long sought after quantum spin liquid state. Its excitations are anyons, particles that can only exist in two dimensions that break the normal fermion/boson dichotomy. Anyons have been the subject of much attention because, among other reasons, there are proposals to braid them through space and time to achieve noise tolerant quantum computations \cite{freedmanTopologicalQuantumComputation2003}. 

Third and perhaps most importantly, it a rare many body interacting quantum system that can be treated analytically. It is exactly solveable meaning that we can explicitly write down its many body ground states in terms of single particle states~\cite{kitaevAnyonsExactlySolved2006}. Its solubility comes about because the model has extensively many conserved degrees of freedom that mediate the interactions between quantum degrees of freedom.

To get down to brass tacks, the Kitaev Honeycomb model is a model of interacting spin$-1/2$s on the vertices of a honeycomb lattice. Each bond in the lattice is assigned a label $\alpha \in \{ x, y, z\}$ and that bond couples its two spin neighbours along the $\alpha$ axis. 

This gives us the Hamiltonian
$$\mathcal{H} =  - \sum_{\langle j,k\rangle_\alpha} J^{\alpha}\sigma_j^{\alpha}\sigma_k^{\alpha},$$
where $\sigma^\alpha_j$ is a Pauli matrix acting on site $j$, \(\langle j,k\rangle_\alpha\) is a pair of nearest-neighbour indices connected by an $\alpha$-bond with exchange coupling $J^\alpha$~\cite{kitaevAnyonsExactlySolved2006}.

% plaquette operators and wilson loops
This model has a set of conserved quantities that, in the spin language, take the form of Wilson loops 
$$W_p = \prod \sigma_j^{\alpha}\sigma_k^{\alpha}$$
following any closed path of the lattice. In this product each pair of spins appears twice with two of the three bonds types, using the spin commutation relations we can replace each pair with the third. For a single hexagonal plaquette this looks like:
$$W_p = \sigma_1^{z}\sigma_2^{z} \sigma_2^{x}\sigma_3^{x} \sigma_3^{y}\sigma_4^{y} \sigma_4^{z}\sigma_5^{z} \sigma_5^{x}\sigma_6^{x} \sigma_6^{y}\sigma_1^{y}$$
$$W_p = \sigma_1^{x}\sigma_2^{y} \sigma_3^{z} \sigma_4^{x} \sigma_5^{y}\sigma_6^{z}$
In this latter form can be seen to commute with all the terms in the Hamiltonian because {\color{red} why again?}

The Hamiltonian commutes with the plaquette operators $W_p$, products of the $K$s around a plaquette. The Ks also commute with one another.
$$W_p = \prod_{<ij> \in P} K_{ij} = K_{12}K_{23}K_{34}K_{56} ... K_{N1}$$

Expanding the bond operators $K_{ij} = \sigma_i^{\alpha} \sigma_j^{\alpha}$, Pauli operators on each site appear in adjacent pairs so can be replaced via $\sigma_i \sigma_j = \delta_{ij} + \epsilon_{ijk} \sigma_k$ giving a product of Pauli matrices associated with the outward pointing bonds from the plaquette. In the general case:
$$W_p = \prod_{i \in P} i (-1)^{c_i} \sigma_i$$
where $c_i = 0,1$ measures the handedness of the edges around vertex i, see Fig \ref{fig:handedness}. Plaquette operators for plaquettes with even numbers of edges square to 1 and hence have eigenvalues $\pm 1$, while those around odd plaquettes have eigenvalues \(\pm i\) breaking chiral symmetry. The values of the plaquette operators partition the Hilbert space of the Hamiltonian into a set of flux sectors.

% relationship between wilson loops and topology
Such paths can enclose a collection of faces or `plaquettes' of the lattice. In the case of periodic boundary conditions, the system is torioidal and we also get Wilson loops that wind the whole system without enclosing a definite area. The loop operator associated with each such path has eigenvalues $/pm 1$ and can be interpreted as measuring the magnetic flux through that region. Without going into the details of counting them, the number of these conserved loop operators clearly scales with system size and it is this extensive number of classical degrees of freedom that ultimately allows us to decouple this interacting many body hamiltonian into a set of non interaction quadratic hamiltonians. {\color{red} add a figure showing the different kinds of Wilson loops and of an example plaquette}

![**(a)** The standard Kitaev Model is defined on a honeycomb lattice. The special feature of the honeycomb lattice that makes the model solveable it is that each vertex is joined by exactly three bonds i.e the lattice is trivalent. One of three labels is assigned to each **(b)** We represent the antisymmetric gauge degree of freedom $u_{jk} = \pm 1$ with arrows that point in the direction $u_{jk} = +1$ **(c)** The majorana transformation can be visualised as breaking each spin into four majoranas which then pair along the bonds. The pairs of x,y and z majoranas become part of the classical $\mathbb{Z}_2$ gauge field $u_{ij}$ leaving just a single majorana $c_i$ per site.](figure_code/amk_chapter/honeycomb_zoom/intro_figure_template){width=100% #fig:honeycomb_zoom}

In order to actually solve the model we need to figure out how to leverage these conserved quantities. The trick is not so much a trick as an almost perfect consequence of the structure of the model and perhaps this was in fact how Kitaev first came up with it. We know that a single spin$-1/2$ can be represented by fermionic creation and annihilation operators $\sigma^{\pm} = 1/2(\sigma^x \pm \sigma^y)$ through a Jordan-Wigner transformation~\cite{}, this gives one fermion for each spin. In turn a fermion can be broken into two Majorana fermions $c_1 = 1/\sqrt{1}(f + f^\dagger)$ and $c_2 = i/\sqrt{1}(f - f^\dagger)$. If we double up the Hilbert space we get four Majoranas per spin: 

