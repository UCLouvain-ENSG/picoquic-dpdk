#include <stdint.h>
struct token_bucket {
    uint64_t rate;
    uint64_t burst;
    uint64_t size;
    long long last_refilled_time;
};

long long get_time_in_ms();

void *init_token_bucket(struct token_bucket *tb, uint64_t rate, uint64_t burst);

void *configure_token_bucket(struct token_bucket *tb, uint64_t rate, uint64_t burst);

int *get_token(struct token_bucket *tb, uint64_t amount);

int wait_until_token_available(struct token_bucket *tb, uint64_t amount);