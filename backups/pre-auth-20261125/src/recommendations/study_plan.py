"""Create and persist a small, revisable study plan from current weak-topic evidence."""
def build_plan(recommendations):
    tasks=[]
    for i,r in enumerate(recommendations[:4]):
        topic=r['topic']; diff=r.get('suggested_difficulty','Easy')
        prerequisite=r.get('prerequisite')
        first=f"Review prerequisite concept: {prerequisite}." if prerequisite else "Review the core concepts."
        tasks.extend([(i*2+1,first,topic),(i*2+2,f"Practice 5 {diff.lower()} questions, review missed answers, then retry a short assessment.",topic)])
    return tasks
