#include "ema_filter.h"

EMAFilter::EMAFilter(double a) {
    alpha = a;
    filtered_value = 0.0;
    initialized = false;
}

void EMAFilter::setAlpha(double a) {
    alpha = a;
}

double EMAFilter::update(double raw_value) {
    if (!initialized) {
        filtered_value = raw_value;
        initialized = true;
    } else {
        filtered_value = alpha * raw_value + (1.0 - alpha) * filtered_value;
    }
    return filtered_value;
}

double EMAFilter::getValue() const {
    return filtered_value;
}

void EMAFilter::reset() {
    initialized = false;
}