import sys
import collections

# --- TASK 1: Import your team's parser ---
try:
    import pnml_parser
except ImportError:
    print("Error: Could not find 'pnml_parser.py'.")
    print("Make sure it's in the same directory as this script.")
    sys.exit(1)


# --- ADAPTER: Converts Task 1's output to Task 2's input ---

def convert_net_to_bfs_format(net: pnml_parser.PetriNet):
    """
    Converts the PetriNet object from the parser into the simple
    set/dict format needed for the BFS algorithm.
    """
    
    # Find the initial marking
    initial_marking_set = {
        p.id for p in net.places.values() if p.initial_marking > 0
    }
    
    # Build the transitions dictionary
    transitions_dict = {}
    
    for t_id in net.transitions.keys():
        transitions_dict[t_id] = {'pre': set(), 'post': set()}
        
    for arc in net.arcs:
        source_id = arc.source
        target_id = arc.target
        
        # P -> T (input to transition)
        if source_id in net.places and target_id in net.transitions:
            transitions_dict[target_id]['pre'].add(source_id)
            
        # T -> P (output from transition)
        elif source_id in net.transitions and target_id in net.places:
            transitions_dict[source_id]['post'].add(target_id)
            
    return initial_marking_set, transitions_dict


# --- TASK 2: Your BFS Algorithm ---

def find_reachable_markings_bfs(start_marking, all_transitions):
    """
    Finds all reachable markings of a 1-safe Petri Net
    using an explicit Breadth-First Search (BFS).
    
    Args:
        start_marking (set): A set of place IDs for the initial marking.
        all_transitions (dict): The net's transition structure.
        
    Returns:
        set: A set of frozensets, where each frozenset is
             a reachable marking.
    """
    
    initial_state = frozenset(start_marking)
    
    visited = set()
    queue = collections.deque()
    
    visited.add(initial_state)
    queue.append(initial_state)
    
    while queue:
        current_marking = queue.popleft() 
        
        for t_id, t_info in all_transitions.items():
            
            pre_set = t_info['pre']
            post_set = t_info['post']
            
            # Step A: Check if the transition is enabled
            if pre_set.issubset(current_marking):
                
                # Step B: Fire the transition & compute next marking
                temp_marking = current_marking - pre_set
                next_marking_set = temp_marking | post_set
                next_marking = frozenset(next_marking_set)

                # Step C: Add the new marking if it's never been seen
                if next_marking not in visited:
                    visited.add(next_marking)
                    queue.append(next_marking)

    return visited

# --- MAIN: Connects everything together ---

def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print(f"  python {sys.argv[0]} <path_to_pnml_file>")
        sys.exit(1)
        
    pnml_file_path = sys.argv[1]
    
    print(f"Parsing PNML file: {pnml_file_path}...")
    try:
        parsed_net = pnml_parser.parse_pnml(pnml_file_path)
    except pnml_parser.PNMLParserError as e:
        print(f"ERROR during parsing:\n{e}")
        sys.exit(1)
    
    print("Parsing complete.")
   
    start_marking_set, transitions_dict = convert_net_to_bfs_format(parsed_net)

    print("Starting BFS to find reachable markings...")
    reachable_set = find_reachable_markings_bfs(start_marking_set, transitions_dict)
 
    print(f"\n--- Task 2 Results ---")
    print(f"Total reachable markings found: {len(reachable_set)}")
    print("All Reachable Markings:")
    
    for i, marking_fs in enumerate(reachable_set):
        marking = set(marking_fs)
        print(f"  {i+1}: {marking or '∅'}")


if __name__ == "__main__":
    main()