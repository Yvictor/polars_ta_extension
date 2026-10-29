# Engulf checked-window static proof

Matched Rust1.97 portable x86 actual postThinLTO objects; no target execution or timing. Both arms retain public wrapper324B. Baseline implementation750B, candidate1097B because the original fallback remains.

Baseline loop +0x100..+0x1e8 branches from +0x103/+0x120 to output/input panic blocks +0x2be/+0x2ab. The candidate window loop +0x16f..+0x229 has exactly one integer comparison (+0x187: loop termination), zero panic relocations, and every branch stays within the loop or exits at +0x32a to write the output range. All original bounds-panic relocations remain outside this region in the fallback beginning +0x229. Relocation presence in the whole function therefore is not a surviving hot-window bounds check. Raw offsets/branches/instructions and source hashes are in fastpath-proof.json.

For a valid public call, i=max(start,2), i<=end, input prefix length=end+1, trip=end-i+1. Each two-bar window starts i-1 and has trip+1 elements, so start+length=end+1 exactly. The output prefix has trip elements, already required by the unchanged public validation/private asserts. INDEX_MAX prevents arithmetic overflow. Every checked get therefore succeeds for a legal nonempty call; failed gets retain the original loop. Empty range/error validation and the four-input OHLC length contract are unchanged.

This establishes code generation only. Extra entry work and code size may regress short workloads; same-runner CI is required before any performance claim or publication.
