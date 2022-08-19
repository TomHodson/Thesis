import numpy as np
from koala.plotting import _lines_cross_unit_cell, _line_fully_in_unit_cell
from koala.lattice import Lattice

def remove_dangling_edges(vertices, edges):
    vertex_indices, vertex_degrees = np.unique(edges.flatten(), return_counts=True)
    degree_one = vertex_indices[vertex_degrees == 1]
    degree_zero = np.setdiff1d(np.arange(len(vertices)), edges.flatten())
    dangling_vertices = np.concatenate([degree_one, degree_zero])
                                 
    # print(dangling_vertices)
    dangling_edges = np.any(np.isin(edges, dangling_vertices), axis = -1)
    edges = edges[~dangling_edges]

    # print(vertices.shape)
    verts_to_keep = np.setdiff1d(np.arange(len(vertices)), dangling_vertices)
    vertices = vertices[verts_to_keep]
    
    for i, v in enumerate(verts_to_keep):
        edges[edges == v] = i

    return vertices, edges, len(dangling_vertices)
    
    

def cut_patch(lattice, factor = 0.1, center = np.array([0.5, 0.5])):
    scaled_verts = (lattice.vertices.positions - center) / factor + center
    
    #figure out which edges are withing the patch
    edge_positions = scaled_verts[lattice.edges.indices]
    needed_lines = _line_fully_in_unit_cell(edge_positions)
    print(lattice, needed_lines.shape)
    
    #get the edges within the patch
    edges = lattice.edges.indices[needed_lines].copy()
    
    #figure out which vertices are needed
    vertices = np.unique(edges.flatten())
    # print(vertices)

    #remap the edges
    for i, v in enumerate(vertices):
        edges[edges == v] = i
        
    vertices = scaled_verts[vertices]
    while True: 
        vertices, edges, n_dangling_vertices = remove_dangling_edges(vertices, edges)
        if n_dangling_vertices == 0: break
        
    
    return Lattice(vertices, edges, np.zeros_like(edges))