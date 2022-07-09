
struct token_bucket {
    unsigned int rate;
    unsigned int burst;
    unsigned int size;
    long long last_refilled_time;
};

long long get_time_in_ms();

void *init_token_bucket(struct token_bucket *tb, unsigned int rate, unsigned int burst);

int *get_token(struct token_bucket *tb, unsigned int amount);