# makefile for building a perl TA.pm module
# CMR (commandline multitheraded release only)
#
# Tested with SWIG v1.3.24, Perl v5.8.4

PERL5_INCLUDE=$(shell perl -V:installarchlib | perl -ne 'print $$1 if m/installarchlib='\''(.*)'\''/')/CORE
INSTDIR=$(shell perl -V:installprivlib | perl -ne 'print $$1 if m/installprivlib='\''(.*)'\''/')
TOPDIR=../../../..
WRAPDIR=$(TOPDIR)/temp/perl/wrap
TEMPDIR=$(TOPDIR)/temp/perl/wrap

CPPFLAGS   = -D_REENTRANT -D_GNU_SOURCE \
	     -DTHREADS_HAVE_PIDS -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64 \
	     -I$(PERL5_INCLUDE) \
	     -I$(TOPDIR)/../c/include
CFLAGS     = -pipe -Wall -Wno-unused -O2 -fno-strict-aliasing -fPIC

####### Support for 64-bit systems
ifeq ($(shell uname -m), x86_64)
    CFLAGS   += -m64 -D__64BIT__
    ifeq ($(shell uname -r | cut -d- -f3-), amd64-k8)
        CFLAGS   += -march=k8
    else
        CFLAGS   += -march=x86-64
    endif
endif

CC         = gcc
LDFLAGS    = -shared -fPIC
LDLIBS     =

all: $(TOPDIR)/lib/perl/TA.so $(TOPDIR)/lib/perl/Finance/TA.pm

clean:
	rm -f $(WRAPDIR)/*.c
	rm -f $(WRAPDIR)/*.pm
	rm -f $(TEMPDIR)/*.o

$(TOPDIR)/lib/perl/TA.so: \
		$(TEMPDIR)/ta_libc_wrap.o \
		$(TOPDIR)/../c/lib/libta_libc_cmr.a
	$(CC) $(LDFLAGS) -o $@ $< \
		$(TOPDIR)/../c/lib/libta_libc_cmr.a $(LDLIBS)

$(TOPDIR)/lib/perl/Finance/TA.pm: \
		$(WRAPDIR)/TA.pm \
		$(TOPDIR)/src/interface/perl.pm
	perl -pe 's/^%(OWNER|ITERATORS)/our %\1/' $(WRAPDIR)/TA.pm >$@
	cat $(TOPDIR)/src/interface/perl.pm >>$@ 

$(WRAPDIR)/TA.pm $(WRAPDIR)/ta_libc_wrap.c: \
		$(TOPDIR)/src/interface/ta_libc.swg \
		$(TOPDIR)/src/interface/ta_libc.perl.swg \
		$(TOPDIR)/src/interface/ta_func.swg
	swig -perl -module "Finance::TA" -proxy -Fstandard -o $(WRAPDIR)/ta_libc_wrap.c \
		-I$(TOPDIR)/src/interface -I$(TOPDIR)/../c/include \
		$<

install: $(INSTDIR)/TA.so $(INSTDIR)/Finance/TA.pm

$(INSTDIR)/TA.so: $(TOPDIR)/lib/perl/TA.so
	cp -f $(TOPDIR)/lib/perl/TA.so $(INSTDIR)/TA.so

$(INSTDIR)/Finance/TA.pm: $(TOPDIR)/lib/perl/Finance/TA.pm
	test -d $(INSTDIR)/Finance || mkdir $(INSTDIR)/Finance
	cp -f $(TOPDIR)/lib/perl/Finance/TA.pm $(INSTDIR)/Finance/TA.pm

.PHONY: all clean install
