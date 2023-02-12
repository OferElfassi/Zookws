ASFLAGS := -m64
CFLAGS  := -m64 -g -std=c99 -Wall -Wno-format-overflow -D_GNU_SOURCE -static
LDFLAGS := -m64
LDLIBS  := 
PROGS   := zookd \
           zookld \
           zookhttp \
           zookd-exstack \
           zookd-nxstack \
           zookd-withssp \
           shellcode.bin \
           run-shellcode

ifeq ($(wildcard /usr/bin/execstack),)
  ifneq ($(wildcard /usr/sbin/execstack),)
    ifeq ($(filter /usr/sbin,$(subst :, ,$(PATH))),)
      PATH := $(PATH):/usr/sbin
    endif
  endif
endif

all: $(PROGS)
.PHONY: all

zookld: zookld.o http.o
	$(CC) $(LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@

zookhttp: zookhttp.o http.o
	$(CC) $(LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@

zookd: zookd.o http.o

zookd-exstack: zookd.o http.o
	$(CC) $(LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@ -z execstack

zookd-nxstack: zookd.o http.o
	$(CC) $(LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@

zookd-withssp: zookd-withssp.o http-withssp.o
	$(CC) $(LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@

run-shellcode: run-shellcode.o
	$(CC) $(LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@

zookld.o: zookld.c http.h

%.o: %.c
	$(CC) $< -c -o $@ $(CFLAGS) -fno-stack-protector

%-withssp.o: %.c
	$(CC) $< -c -o $@ $(CFLAGS)

%.bin: %.o
	objcopy -S -O binary -j .text $< $@

.PHONY: clean
clean:
	rm -f *.o *.pyc *.bin $(PROGS)