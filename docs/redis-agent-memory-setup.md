# Set up Redis Agent Memory

Create the Redis Agent Memory service the workshop uses, and collect the values for your `.env`. When you are done, go back to the [README](../README.md#4-check-it) to check your setup.

These steps follow the [quickstart](https://redis.io/docs/latest/develop/ai/context-engine/agent-memory/quickstart/?utm_source=devrel&utm_medium=workshop).

## Create a Redis database

The service needs an active Redis Cloud database, with a public endpoint, Redis Search and the default user enabled. If you don't have one, [create a database](https://redis.io/docs/latest/operate/rc/databases/create-database/?utm_source=devrel&utm_medium=workshop).

Once it exists, copy its public endpoint and the password of the default user from the [Redis Cloud console](https://cloud.redis.io/), and put them together as `redis://default:<password>@<endpoint>`. This is your `REDIS_URL`, which the semantic cache uses later.

## Create a Redis Agent Memory service

**Create the service.** In the [Redis Cloud console](https://cloud.redis.io/), choose **Agent Memory** under **Iris**, then **Create Agent Memory service** and **Customize settings**. Enter a name, pick the database and its `default` user, and under **Memory configuration** enter:

| Setting | Value |
|---|---|
| Short-term TTL | 1 day |
| Long-term TTL | 365 days |
| Extraction cadence | 5 minutes |

Choose **Create**.

Next, **create an API key.** On the service's **Configuration** tab, choose **Create API key** and copy the key. The console shows it only once. This is your `IRIS_AGENT_MEMORY_API_KEY`.

**Copy the connection details.** On the same tab, copy the **URL** (`IRIS_AGENT_MEMORY_URL`) and the **Store ID** (`IRIS_AGENT_MEMORY_STORE_ID`).

### Add a memory type for traveler preferences

In the console, open **Memory types & extraction** and choose **Add type**. Create it from the conversation, with these settings:

| Setting | Value |
|---|---|
| Name | `traveler_preference` |
| Description | Lasting travel preferences and standing instructions for a traveler |
| Extraction prompt | Extract a traveler preference only when the user explicitly states something stable about themselves: a lasting travel preference, a constraint such as a dietary requirement, or a standing instruction. Preserve explicit dietary requirements and food preferences. Put anything that does not fit another field under standing_instructions. Do not keep passwords, access tokens, recovery codes, passport or ID numbers, payment card information, or booking confirmation codes in long-term memory. Do not keep what the assistant said or suggested, or weather or other facts about a place. Ignore transient task details, which belong to the current session only and must not become long-term memories: a destination they are interested in or about to visit ("I want to go to Goa", "I'm going to San Francisco next month"), trip dates, questions about places or the weather ("what is the weather like in Bengaluru?"), and requests for a plan or recommendation. Do not infer a preference from what the user only asked about. Keep only what the traveler states about themselves: lasting preferences, and trips they say they took.

| Field | Type | Description |
|---|---|---|
| `interests` | `list[str]` | Interests from this list: food, landmarks, offbeat, slow, outdoors, nightlife, culture |
| `budget` | `str` | One of low, mid or high |
| `group_size` | `str` | One of solo, pair, family or group |
| `food_and_dietary` | `list[str]` | Dietary requirements and food preferences, such as vegetarian, nut allergy or loves street food |
| `standing_instructions` | `list[str]` | Rules to apply every time, such as "always include a rest day" or "avoid long walks" |

### Summarization and sensitive-data exclusions

| Setting | Suggested value |
|---|---|
| Automatic summarization | After about 12 messages, keeping the most recent 6 |
| Sensitive-data exclusions | Turn on **Semantic exclusions**, with the exclusion prompt below |

```text
Do not keep passwords, access tokens, recovery codes, passport or ID numbers, payment card information, or booking confirmation codes in long-term memory. Do not keep what the assistant said or suggested, or weather or other facts about a place. Ignore transient task details, which belong to the current session only and must not become long-term memories: a destination they are interested in or about to visit ("I want to go to Goa", "I'm going to San Francisco next month"), trip dates, questions about places or the weather ("what is the weather like in Bengaluru?"), and requests for a plan or recommendation. Do not infer a preference from what the user only asked about. Keep only what the traveler states about themselves: lasting preferences, and trips they say they took.
```

This is advisory: it steers what the service extracts, and does not guarantee it.
