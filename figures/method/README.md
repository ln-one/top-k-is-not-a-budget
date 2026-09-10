# DiBud overview

Editable source: dibud.drawio. Compact single-column overview using Paul Tol Vibrant blue (#0077BB) and orange (#EE7733). Inserted as Figure 1 in the method section.

Caption: DiBud directly bounds sorted accesses by B and appends every newly certified position. When the next position remains unresolved, selection prioritizes the sole missing channel of the highest-upper-bound observed competitor if its upper bound is at least the unseen bound. Otherwise it selects the available channel with maximal unread-bound reduction Δ_i, as defined in Section 2.3. Reads stop at B or when both channels are exhausted; the accumulated exact prefix is returned. K is not preset.

The rule card includes both the primary selection branch and its fallback; it does not assume that Sparse is always selected. The certification block includes bound updates and repeated certification before further reads. Budget blocks and list cells are schematic, not measured query outcomes. Each filled budget block denotes one access in the illustrated unit-access case.

Revision: selector explicitly chooses D or S, with separate dashed control arrows to both ranked lists. Solid arrows carry the selected entry to reading and certification. Current competition feeds back to the selector. Budget B gates Read directly.

Latest revision: Dense (blue #0077BB) and Sparse (teal #009988) share one ranked-list container. One dashed selector arrow chooses a channel within that container. Budget uses orange #EE7733; processing/output use neutral gray. Supersedes earlier separate selector arrows.
