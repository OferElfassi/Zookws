ASFLAGS :=
CFLAGS  := -m64 -g -std=c99 -Wall -Wno-format-overflow -D_GNU_SOURCE
LDFLAGS := -m64
LDLIBS  :=
PROGS   := zookd \
           zookld \
           zookhttp
#           zookd-exstack \
#           zookld-exstack\
#           zookhttp-exstack\
#           zookd-nxstack \
#           zookd-withssp \
#           shellcode.bin \
#           run-shellcode

ifeq ($(wildcard /usr/bin/execstack),)
  ifneq ($(wildcard /usr/sbin/execstack),)
    ifeq ($(filter /usr/sbin,$(subst :, ,$(PATH))),)
      PATH := $(PATH):/usr/sbin
    endif
  endif
endif

all: $(PROGS)
.PHONY: all

zookld-exstack.o: zookld-exstack.c http.h
zookld-exstack: zookld-exstack.o http.o
	$(CC) $(LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@

zookld.o: zookld.c http.h
zookld: zookld.o http.o
	$(CC) $(LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@

zookhttp.o: zookhttp.c http.h
zookhttp: zookhttp.o http.o
	$(CC) $(LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@

zookd.o: zookd.c http.h
zookd: zookd.o http.o
	$(CC) $(LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@

zookd-exstack: zookd.o http.o
	$(CC) $(LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@ -z execstack

zookhttp-exstack: zookhttp.o http.o
	$(CC) $(LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@ -z execstack

zookd-nxstack: zookd.o http.o
	$(CC) $(LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@

zookd-withssp: zookd-withssp.o http-withssp.o
	$(CC) $(LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@

run-shellcode: run-shellcode.o
	$(CC) $(LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@

%.o: %.c
	$(CC) $< -c -o $@ $(CFLAGS) -fno-stack-protector

%-withssp.o: %.c
	$(CC) $< -c -o $@ $(CFLAGS)

%.bin: %.o
	objcopy -S -O binary -j .text $< $@

.PHONY: clean
clean:
	rm -f *.o *.pyc *.bin $(PROGS)