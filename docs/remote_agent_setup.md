# Connecting an agent on another machine to the mailbox

**Purpose.** The teacher and neural-baseline work (lane C) runs on a machine with a GPU. Its agent needs the same mailbox the other agents use, so that ClaudeScope can assign and review its work.

**How it works.** The mailbox is a small program on this host that talks over standard input and output. The remote agent starts it through SSH. A dedicated SSH key is locked to that one program, so the key can do nothing else on this host: no shell, no file access, no port forwarding. No new network port is opened.

Names used below; replace the two placeholders:

- `HOST`: the address at which the remote machine can reach this host by SSH.
- The mailbox address for the remote agent is `trainer`.

## Step 1 · on the remote machine: make a key for the mailbox only

```bash
ssh-keygen -t ed25519 -f ~/.ssh/mailbox_key -N "" -C "mailbox-trainer"
cat ~/.ssh/mailbox_key.pub
```

The second command prints one line starting `ssh-ed25519`. Copy it.

## Step 2 · on this host: allow that key to run the mailbox and nothing else

Add **one line** to `/home/derp/.ssh/authorized_keys`: the text below, followed by a space and the line you copied.

```text
command="/usr/bin/python3 /home/derp/sp/learning_mcp/relay.py serve trainer",no-port-forwarding,no-agent-forwarding,no-X11-forwarding,no-pty,no-user-rc
```

So the finished line looks like `command="…serve trainer",no-port-forwarding,…,no-user-rc ssh-ed25519 AAAA… mailbox-trainer`.

## Step 3 · on the remote machine: test the link without any agent

```bash
printf '%s\n' '{"jsonrpc":"2.0","id":0,"method":"initialize","params":{}}' \
  | ssh -i ~/.ssh/mailbox_key -o BatchMode=yes -o IdentitiesOnly=yes -T derp@HOST
```

Success is one line of JSON containing `"Your mailbox address is trainer"`. The first connection asks you to accept this host's key; answer yes once, by running `ssh -i ~/.ssh/mailbox_key -o IdentitiesOnly=yes -T derp@HOST` by hand and pressing Ctrl-D.

## Step 4 · on the remote machine: register the mailbox with the agent

For Claude Code:

```bash
claude mcp add --transport stdio --scope user learning_mailbox -- \
  ssh -i ~/.ssh/mailbox_key -o BatchMode=yes -o IdentitiesOnly=yes -T derp@HOST
```

For Codex:

```bash
codex mcp add learning_mailbox -- \
  ssh -i ~/.ssh/mailbox_key -o BatchMode=yes -o IdentitiesOnly=yes -T derp@HOST
```

Then start the agent and check `/mcp`: `learning_mailbox` should be connected and its instructions should say the address is `trainer`.

## Step 5 · first message

Give the remote agent this prompt:

> You are the lane C agent for the semantic parser project; your mailbox address is trainer. Use learning_mailbox to send claude the message "trainer online", then read your inbox and follow the instructions from claude.

## If it fails

| Symptom | Likely cause |
| --- | --- |
| `Connection refused` or a timeout in step 3 | This host is not reachable from the remote machine on port 22. Tell ClaudeScope; the alternative is a tunnel opened from this side. |
| `Permission denied (publickey)` | The line in step 2 is broken across two lines, or was added for a different user. |
| A shell prompt appears in step 3 | The `command="…"` prefix is missing from the line in step 2. Remove the line and add it again; as it stands the key gives full access. |
| The JSON says a different address | Another key is being offered. Keep `-o IdentitiesOnly=yes`. |

## What the key can and cannot do

- It can send mailbox messages as `trainer` and read `trainer`'s inbox.
- It cannot run commands, read files, or forward ports on this host.
- Messages from `trainer` are read by the other agents as mail from a peer. If the remote machine were compromised, its mailbox could be used to send them misleading text. Remove the line from `authorized_keys` to cut the link.

## Moving files

The mailbox carries short messages only (4,000 characters). Data and code move through the project's Git repository, which the remote machine clones. API keys stay on the remote machine: never in the repository and never in a mailbox message.
