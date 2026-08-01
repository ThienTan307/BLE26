#ifndef EMA_FILTER_H
#define EMA_FILTER_H

class EMAFilter {
private:
    double alpha;
    double filtered_value;
    bool initialized;

public:
    EMAFilter(double a = 0.2);
    void setAlpha(double a);
    double update(double raw_value);
    double getValue() const;
    void reset();
};

#endif