#include "token_bucket.h"
#include <sys/time.h>
#include <stddef.h>

long long get_time_in_ms(){
    struct timeval time;
    gettimeofday(&time, NULL);
    long long curr_time_in_ms = time.tv_sec*1000LL + time.tv_usec/1000;
    return curr_time_in_ms;
}

void *init_token_bucket(struct token_bucket *tb, uint64_t rate, uint64_t burst){
    tb->rate = rate;
    tb->burst = burst;
    tb->size = burst;
    tb->last_refilled_time = get_time_in_ms();
}
int *get_token(struct token_bucket *tb, uint64_t amount){

    if (tb->size < amount){
        long long curr_time = get_time_in_ms();
        if(curr_time > tb->last_refilled_time){
            long long elapsed_time = (long long) curr_time - tb->last_refilled_time;
            tb->size += elapsed_time*tb->rate;
            tb->last_refilled_time = curr_time;
        }
    }
    if(tb->size < amount){
        return 0;
    }
    tb->size -= amount;
    return 1;
}

int wait_until_token_available(struct token_bucket *tb, unsigned amount){

    //busy wait
    while(!get_token(tb,amount));
    return 0;
}