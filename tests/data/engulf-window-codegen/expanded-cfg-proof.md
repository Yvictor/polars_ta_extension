# Entry / window / fallback branch table

Both candidate fallback loops are whitespace-normalized exact copies of the original433 generated loop; normalized SHA256 374bd3e9fa16a9ea4ab5ef56ebd9f8c68915a3eefbc2e2f0446cde560e949099.

Panic-bounds relocation offsets: 0x415, 0x425, 0x435, 0x445. All incoming panic-block branches originate in fallback, never in the window loop. Entry get guards branch to fallback when a cut fails; successful cuts enter window loop.

| offset | branch | target | source | target class |
|---|---|---|---|---|
| 0x12 | jb | 0x332 | entry | other_entry_or_assert |
| 0x37 | je | 0x341 | entry | other_entry_or_assert |
| 0x4e | je | 0x35a | entry | other_entry_or_assert |
| 0x65 | je | 0x373 | entry | other_entry_or_assert |
| 0x81 | je | 0x38c | entry | other_entry_or_assert |
| 0xa0 | jae | 0x3a5 | entry | other_entry_or_assert |
| 0xa9 | je | 0x3b1 | entry | other_entry_or_assert |
| 0xbd | jae | 0xd2 | entry | other_entry_or_assert |
| 0xcd | jmp | 0x330 | entry | other_entry_or_assert |
| 0xd5 | jae | 0x3ca | entry | other_entry_or_assert |
| 0xde | jae | 0x3df | entry | other_entry_or_assert |
| 0xfb | jae | 0x112 | entry | other_entry_or_assert |
| 0x10b | jbe | 0x139 | entry | other_entry_or_assert |
| 0x10d | jmp | 0x229 | entry | fallback |
| 0x133 | ja | 0x229 | entry | fallback |
| 0x13c | je | 0x229 | entry | fallback |
| 0x145 | je | 0x229 | entry | fallback |
| 0x152 | ja | 0x3f1 | entry | other_entry_or_assert |
| 0x15b | je | 0x328 | entry | other_entry_or_assert |
| 0x16d | jmp | 0x190 | entry | window_hot |
| 0x18a | je | 0x32a | window_hot | range_write_exit |
| 0x1b1 | jae | 0x1e0 | window_hot | window_hot |
| 0x1b7 | jb | 0x180 | window_hot | window_hot |
| 0x1bd | jb | 0x1c5 | window_hot | window_hot |
| 0x1c3 | ja | 0x200 | window_hot | window_hot |
| 0x1c9 | jbe | 0x180 | window_hot | window_hot |
| 0x1cf | jae | 0x200 | window_hot | window_hot |
| 0x1d1 | jmp | 0x180 | window_hot | window_hot |
| 0x1e4 | jae | 0x180 | window_hot | window_hot |
| 0x1ea | jbe | 0x1f2 | window_hot | window_hot |
| 0x1f0 | jae | 0x200 | window_hot | window_hot |
| 0x1f6 | jb | 0x180 | window_hot | window_hot |
| 0x1fc | jbe | 0x180 | window_hot | window_hot |
| 0x204 | jne | 0x20c | window_hot | window_hot |
| 0x206 | jnp | 0x16f | window_hot | window_hot |
| 0x210 | jne | 0x218 | window_hot | window_hot |
| 0x212 | jnp | 0x16f | window_hot | window_hot |
| 0x224 | jmp | 0x180 | window_hot | window_hot |
| 0x239 | jmp | 0x260 | fallback | fallback |
| 0x246 | jae | 0x419 | fallback | panic_bounds |
| 0x25a | jae | 0x32a | fallback | range_write_exit |
| 0x263 | ja | 0x406 | fallback | panic_bounds |
| 0x287 | jae | 0x2b0 | fallback | fallback |
| 0x28d | jb | 0x240 | fallback | fallback |
| 0x293 | jb | 0x29b | fallback | fallback |
| 0x299 | ja | 0x2e0 | fallback | fallback |
| 0x29f | jbe | 0x240 | fallback | fallback |
| 0x2a5 | jae | 0x2e0 | fallback | fallback |
| 0x2a7 | jmp | 0x240 | fallback | fallback |
| 0x2b4 | jae | 0x240 | fallback | fallback |
| 0x2ba | jbe | 0x2c2 | fallback | fallback |
| 0x2c0 | jae | 0x2e0 | fallback | fallback |
| 0x2c6 | jb | 0x240 | fallback | fallback |
| 0x2d0 | jbe | 0x240 | fallback | fallback |
| 0x2e4 | jne | 0x2e8 | fallback | fallback |
| 0x2e6 | jnp | 0x30c | fallback | fallback |
| 0x2ec | jne | 0x2f0 | fallback | fallback |
| 0x2ee | jnp | 0x30c | fallback | fallback |
| 0x2f3 | jae | 0x439 | fallback | panic_bounds |
| 0x307 | jmp | 0x24c | fallback | fallback |
| 0x30f | jae | 0x429 | fallback | panic_bounds |
| 0x323 | jmp | 0x24c | fallback | fallback |
| 0x3ab | jne | 0xaf | exit_or_panic | other_entry_or_assert |
