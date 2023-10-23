//
// Created by Borchers, Henry Samuel on 6/8/18.
//

#ifndef PYEXIV2BIND_GLUE_EXECEPTIONS_H
#define PYEXIV2BIND_GLUE_EXECEPTIONS_H

#include <exception>

class NoIccError: public std::exception{
public:
    virtual const char *what() const throw(){
        return "No ICC profile found";
    }
};
#endif //PYEXIV2BIND_GLUE_EXECEPTIONS_H
