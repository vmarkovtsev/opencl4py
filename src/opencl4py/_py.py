"""
Copyright (c) 2014, Samsung Electronics Co.,Ltd.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of Samsung Electronics Co.,Ltd..
"""

"""
opencl4py - OpenCL cffi bindings and helper classes.
URL: https://github.com/ajkxyz/opencl4py
Original author: Alexey Kazantsev <a.kazantsev@samsung.com>
"""

"""
Helper classes for OpenCL cffi bindings.
"""
import opencl4py._cffi as cl


class CLRuntimeError(RuntimeError):
    def __init__(self, msg, code):
        super(CLRuntimeError, self).__init__(msg)
        self.code = code


class CL(object):
    """Base OpenCL class.

    Attributes:
        _lib: handle to cffi.FFI object.
        _handle: cffi handle to OpenCL object.
    """

    ERRORS = {
        0:   "CL_SUCCESS",
        - 1:  "CL_DEVICE_NOT_FOUND",
        - 2:  "CL_DEVICE_NOT_AVAILABLE",
        - 3:  "CL_COMPILER_NOT_AVAILABLE",
        - 4:  "CL_MEM_OBJECT_ALLOCATION_FAILURE",
        - 5:  "CL_OUT_OF_RESOURCES",
        - 6:  "CL_OUT_OF_HOST_MEMORY",
        - 7:  "CL_PROFILING_INFO_NOT_AVAILABLE",
        - 8:  "CL_MEM_COPY_OVERLAP",
        - 9:  "CL_IMAGE_FORMAT_MISMATCH",
        - 10: "CL_IMAGE_FORMAT_NOT_SUPPORTED",
        - 11: "CL_BUILD_PROGRAM_FAILURE",
        - 12: "CL_MAP_FAILURE",
        - 13: "CL_MISALIGNED_SUB_BUFFER_OFFSET",
        - 14: "CL_EXEC_STATUS_ERROR_FOR_EVENTS_IN_WAIT_LIST",
        - 15: "CL_COMPILE_PROGRAM_FAILURE",
        - 16: "CL_LINKER_NOT_AVAILABLE",
        - 17: "CL_LINK_PROGRAM_FAILURE",
        - 18: "CL_DEVICE_PARTITION_FAILED",
        - 19: "CL_KERNEL_ARG_INFO_NOT_AVAILABLE",

        - 30: "CL_INVALID_VALUE",
        - 31: "CL_INVALID_DEVICE_TYPE",
        - 32: "CL_INVALID_PLATFORM",
        - 33: "CL_INVALID_DEVICE",
        - 34: "CL_INVALID_CONTEXT",
        - 35: "CL_INVALID_QUEUE_PROPERTIES",
        - 36: "CL_INVALID_COMMAND_QUEUE",
        - 37: "CL_INVALID_HOST_PTR",
        - 38: "CL_INVALID_MEM_OBJECT",
        - 39: "CL_INVALID_IMAGE_FORMAT_DESCRIPTOR",
        - 40: "CL_INVALID_IMAGE_SIZE",
        - 41: "CL_INVALID_SAMPLER",
        - 42: "CL_INVALID_BINARY",
        - 43: "CL_INVALID_BUILD_OPTIONS",
        - 44: "CL_INVALID_PROGRAM",
        - 45: "CL_INVALID_PROGRAM_EXECUTABLE",
        - 46: "CL_INVALID_KERNEL_NAME",
        - 47: "CL_INVALID_KERNEL_DEFINITION",
        - 48: "CL_INVALID_KERNEL",
        - 49: "CL_INVALID_ARG_INDEX",
        - 50: "CL_INVALID_ARG_VALUE",
        - 51: "CL_INVALID_ARG_SIZE",
        - 52: "CL_INVALID_KERNEL_ARGS",
        - 53: "CL_INVALID_WORK_DIMENSION",
        - 54: "CL_INVALID_WORK_GROUP_SIZE",
        - 55: "CL_INVALID_WORK_ITEM_SIZE",
        - 56: "CL_INVALID_GLOBAL_OFFSET",
        - 57: "CL_INVALID_EVENT_WAIT_LIST",
        - 58: "CL_INVALID_EVENT",
        - 59: "CL_INVALID_OPERATION",
        - 60: "CL_INVALID_GL_OBJECT",
        - 61: "CL_INVALID_BUFFER_SIZE",
        - 62: "CL_INVALID_MIP_LEVEL",
        - 63: "CL_INVALID_GLOBAL_WORK_SIZE",
        - 64: "CL_INVALID_PROPERTY",
        - 65: "CL_INVALID_IMAGE_DESCRIPTOR",
        - 66: "CL_INVALID_COMPILER_OPTIONS",
        - 67: "CL_INVALID_LINKER_OPTIONS",
        - 68: "CL_INVALID_DEVICE_PARTITION_COUNT",
    }

    def __init__(self):
        self._lib = cl.lib  # to hold the reference
        self._handle = None

    @property
    def handle(self):
        """Returns cffi handle to OpenCL object.
        """
        return self._handle

    @staticmethod
    def extract_ptr_and_size(host_array, size):
        """Returns cffi pointer to host_array and its size.
        """
        if hasattr(host_array, "__array_interface__"):
            host_ptr = host_array.__array_interface__["data"][0]
            if size is None:
                size = host_array.nbytes
        else:
            host_ptr = host_array
            if size is None:
                raise ValueError("size should be set "
                                 "in case of non-numpy host_array")
        return (cl.NULL if host_ptr is None
                else cl.ffi.cast("void*", host_ptr), size)

    @staticmethod
    def get_wait_list(wait_for):
        """Returns cffi event list and number of events
        from list of Event objects, returns (None, 0) if wait_for is None.
        """
        if wait_for is not None:
            n_events = len(wait_for)
            wait_list = cl.ffi.new("cl_event[]", n_events)
            for i, ev in enumerate(wait_for):
                wait_list[i] = ev.handle
        else:
            n_events = 0
            wait_list = cl.NULL
        return (wait_list, n_events)

    @staticmethod
    def get_error_name_from_code(code):
        return CL.ERRORS.get(code, "UNKNOWN")

    @staticmethod
    def get_error_description(code):
        return "%s (%d)" % (CL.get_error_name_from_code(code), code)


class Event(CL):
    """Holds OpenCL event.

    Attributes:
        profiling_values:
            dictionary of profiling values
            if get_profiling_info was ever called;
            keys: CL_PROFILING_COMMAND_QUEUED,
                  CL_PROFILING_COMMAND_SUBMIT,
                  CL_PROFILING_COMMAND_START,
                  CL_PROFILING_COMMAND_END;
            values: the current device time counter in seconds (float),
                    or 0 if there was an error, in such case, corresponding
                    profile_errors will be set with the error code.
        profiling_errors: dictionary of profiling errors
                          if get_profiling_info was ever called.
    """
    def __init__(self, handle):
        super(Event, self).__init__()
        self._handle = handle

    @staticmethod
    def wait_multi(wait_for, lib=cl.lib):
        """Wait on list of Event objects.
        """
        wait_list, n_events = CL.get_wait_list(wait_for)
        n = lib.clWaitForEvents(n_events, wait_list)
        if n:
            raise CLRuntimeError("clWaitForEvents() failed with "
                                 "error %s" % CL.get_error_description(n), n)

    def wait(self):
        """Waits on this event.
        """
        Event.wait_multi((self,), self._lib)

    def get_profiling_info(self, raise_exception=True):
        """Get profiling info of the event.

        Queue should be created with CL_QUEUE_PROFILING_ENABLE flag,
        and event should be in complete state (wait completed).

        Parameters:
            raise_exception: raise exception on error or not,
                             self.profiling_values, self.profiling_errors
                             will be available anyway.

        Returns:
            tuple of (profiling_values, profiling_errors).
        """
        vle = cl.ffi.new("cl_ulong[]", 1)
        sz = cl.ffi.sizeof(vle)
        vles = {}
        errs = {}
        for name in (cl.CL_PROFILING_COMMAND_QUEUED,
                     cl.CL_PROFILING_COMMAND_SUBMIT,
                     cl.CL_PROFILING_COMMAND_START,
                     cl.CL_PROFILING_COMMAND_END):
            vle[0] = 0
            n = self._lib.clGetEventProfilingInfo(
                self.handle, name, sz, vle, cl.NULL)
            vles[name] = 1.0e-9 * vle[0] if not n else 0.0
            errs[name] = n
        self.profiling_values = vles
        self.profiling_errors = errs
        if raise_exception:
            for err in errs.values():
                if not err:
                    continue
                raise CLRuntimeError(
                    "clGetEventProfilingInfo() failed with "
                    "error %s" % CL.get_error_description(err), err)
        return (vles, errs)

    def release(self):
        if self.handle is not None:
            self._lib.clReleaseEvent(self.handle)
            self._handle = None

    def __del__(self):
        self.release()


class Queue(CL):
    """Holds OpenCL command queue.

    Attributes:
        context: context associated with this queue.
        device: device associated with this queue.
    """
    def __init__(self, context, device, flags):
        super(Queue, self).__init__()
        self._context = context
        self._device = device
        err = cl.ffi.new("cl_int *")
        self._handle = self._lib.clCreateCommandQueue(
            context.handle, device.handle, flags, err)
        if err[0]:
            self._handle = None
            raise CLRuntimeError("clCreateCommandQueue() failed with "
                                 "error %s" %
                                 CL.get_error_description(err[0]),
                                 err[0])

    @property
    def context(self):
        """
        context associated with this queue.
        """
        return self._context

    @property
    def device(self):
        """
        device associated with this queue.
        """
        return self._device

    def execute_kernel(self, kernel, global_size, local_size,
                       global_offset=None, wait_for=None, need_event=True):
        """Executes OpenCL kernel (calls clEnqueueNDRangeKernel).

        Parameters:
            kernel: Kernel object.
            global_size: global size.
            local_size: local size.
            global_offset: global offset.
            wait_for: list of the Event objects to wait.
            need_event: return Event object or not.

        Returns:
            Event object or None if need_event == False.
        """
        event = cl.ffi.new("cl_event[]", 1) if need_event else cl.NULL
        wait_list, n_events = CL.get_wait_list(wait_for)
        n_dims = len(global_size)
        global_work_size = cl.ffi.new("size_t[]", n_dims)
        for i, sz in enumerate(global_size):
            global_work_size[i] = sz
        if local_size is None:
            local_work_size = cl.NULL
        else:
            if len(local_size) != n_dims:
                raise ValueError("local_size should be the same length "
                                 "as global_size")
            local_work_size = cl.ffi.new("size_t[]", n_dims)
            for i, sz in enumerate(local_size):
                local_work_size[i] = sz
        if global_offset is None:
            global_work_offset = cl.NULL
        else:
            if len(global_work_offset) != n_dims:
                raise ValueError("global_offset should be the same length "
                                 "as global_size")
            global_work_offset = cl.ffi.new("size_t[]", n_dims)
            for i, sz in enumerate(global_offset):
                global_work_offset[i] = sz
        n = self._lib.clEnqueueNDRangeKernel(
            self.handle, kernel.handle, n_dims, global_work_offset,
            global_work_size, local_work_size, n_events, wait_list, event)
        if n:
            raise CLRuntimeError("clEnqueueNDRangeKernel() failed with "
                                 "error %s" % CL.get_error_description(n), n)
        return Event(event[0]) if event != cl.NULL else None

    def map_buffer(self, buf, flags, size, blocking=True, offset=0,
                   wait_for=None, need_event=False):
        """Maps buffer.

        Parameters:
            buf: Buffer object.
            flags: mapping flags.
            size: mapping size.
            offset: mapping offset.
            wait_for: list of the Event objects to wait.
            need_event: return Event object or not.

        Returns:
            (event, ptr): event - Event object or None if need_event == False,
                          ptr - pointer to the mapped buffer
                                (cffi void* converted to int).
        """
        err = cl.ffi.new("cl_int *")
        event = cl.ffi.new("cl_event[]", 1) if need_event else cl.NULL
        wait_list, n_events = CL.get_wait_list(wait_for)
        ptr = self._lib.clEnqueueMapBuffer(
            self.handle, buf.handle, blocking, flags, offset, size,
            n_events, wait_list, event, err)
        if err[0]:
            raise CLRuntimeError("clEnqueueMapBuffer() failed with error %s" %
                                 CL.get_error_description(err[0]), err[0])
        return (None if event == cl.NULL else Event(event[0]),
                int(cl.ffi.cast("size_t", ptr)))

    def unmap_buffer(self, buf, ptr, wait_for=None, need_event=True):
        """Unmaps previously mapped buffer.

        Parameters:
            buf: Buffer object to unmap.
            ptr: pointer to the mapped buffer.
            wait_for: list of the Event objects to wait.
            need_event: return Event object or not.

        Returns:
            Event object or None if need_event == False.
        """
        event = cl.ffi.new("cl_event[]", 1) if need_event else cl.NULL
        wait_list, n_events = CL.get_wait_list(wait_for)
        n = self._lib.clEnqueueUnmapMemObject(
            self.handle, buf.handle, cl.ffi.cast("void*", ptr),
            n_events, wait_list, event)
        if n:
            raise CLRuntimeError("clEnqueueUnmapMemObject() failed with "
                                 "error %s" % CL.get_error_description(n), n)
        return Event(event[0]) if event != cl.NULL else None

    def read_buffer(self, buf, host_array, blocking=True, size=None, offset=0,
                    wait_for=None, need_event=False):
        """Copies from device buffer to host buffer.

        Parameters:
            buf: Buffer object.
            host_array: numpy array.
            blocking: if the read is blocking.
            size: size in bytes to copy (None for entire numpy array).
            offset: offset in the device buffer.
            wait_for: list of the Event objects to wait.
            need_event: return Event object or not.

        Returns:
            Event object or None if need_event == False.
        """
        event = cl.ffi.new("cl_event[]", 1) if need_event else cl.NULL
        wait_list, n_events = CL.get_wait_list(wait_for)
        host_ptr, size = CL.extract_ptr_and_size(host_array, size)
        n = self._lib.clEnqueueReadBuffer(
            self.handle, buf.handle, blocking, offset, size, host_ptr,
            n_events, wait_list, event)
        if n:
            raise CLRuntimeError("clEnqueueReadBuffer() failed with "
                                 "error %s" % CL.get_error_description(n), n)
        return Event(event[0]) if event != cl.NULL else None

    def write_buffer(self, buf, host_array, blocking=True, size=None, offset=0,
                     wait_for=None, need_event=False):
        """Copies from host buffer to device buffer.

        Parameters:
            buf: Buffer object.
            host_array: numpy array.
            blocking: if the read is blocking.
            size: size in bytes to copy (None for entire numpy array).
            offset: offset in the device buffer.
            wait_for: list of the Event objects to wait.
            need_event: return Event object or not.

        Returns:
            Event object or None if need_event == False.
        """
        event = cl.ffi.new("cl_event[]", 1) if need_event else cl.NULL
        wait_list, n_events = CL.get_wait_list(wait_for)
        host_ptr, size = CL.extract_ptr_and_size(host_array, size)
        n = self._lib.clEnqueueWriteBuffer(
            self.handle, buf.handle, blocking, offset, size, host_ptr,
            n_events, wait_list, event)
        if n:
            raise CLRuntimeError("clEnqueueReadBuffer() failed with "
                                 "error %s" % CL.get_error_description(n), n)
        return Event(event[0]) if event != cl.NULL else None

    def flush(self):
        """Flushes the queue.
        """
        n = self._lib.clFlush(self.handle)
        if n:
            raise CLRuntimeError("clFlush() failed with error %s" %
                                 CL.get_error_description(n), n)

    def finish(self):
        """Waits for all previous commands issued to this queue to end.
        """
        n = self._lib.clFinish(self.handle)
        if n:
            raise CLRuntimeError("clFinish() failed with error %s" %
                                 CL.get_error_description(n), n)

    def release(self):
        if self.handle is not None:
            self._lib.clReleaseCommandQueue(self.handle)
            self._handle = None

    def __del__(self):
        self.release()


class Buffer(CL):
    """Holds OpenCL buffer.

    Attributes:
        context: Context object associated with this buffer.
        flags: flags supplied for the creation of this buffer.
        host_array: host array reference, such as numpy array,
                    will be stored only if flags include CL_MEM_USE_HOST_PTR.
        size: size of the host array.
    """
    def __init__(self, context, flags, host_array, size=None):
        super(Buffer, self).__init__()
        self._context = context
        self._flags = flags
        self._host_array = (host_array if flags & cl.CL_MEM_USE_HOST_PTR != 0
                            else None)
        host_ptr, size = CL.extract_ptr_and_size(host_array, size)
        err = cl.ffi.new("cl_int *")
        self._handle = self._lib.clCreateBuffer(
            context.handle, flags, size, host_ptr, err)
        if err[0]:
            self._handle = None
            raise CLRuntimeError("clCreateBuffer() failed with error %s" %
                                 CL.get_error_description(err[0]),
                                 err[0])

    @property
    def context(self):
        """
        Context object associated with this buffer.
        """
        return self._context

    @property
    def flags(self):
        """
        Flags supplied for the creation of this buffer.
        """
        return self._flags

    @property
    def host_array(self):
        """
        Host array reference, such as numpy array,
        will be stored only if flags include CL_MEM_USE_HOST_PTR.
        """
        return self._host_array

    @property
    def size(self):
        """
        Size of the host array.
        """
        return self._size

    def release(self):
        if self.handle is not None:
            self._lib.clReleaseMemObject(self.handle)
            self._handle = None

    def __del__(self):
        self.release()


class skip(object):
    """A marker to skip setting arguments in Kernel.set_args.
    Passing in the class type makes set_args to skip setting one argument;
    passing skip(n) makes set_args skip n arguments.
    """
    def __init__(self, number):
        self.number = number

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, value):
        if value < 1:
            raise ValueError("number must be greater than 0")
        self._number = value


class Kernel(CL):
    """Holds OpenCL kernel.

    Attributes:
        program: Program object associated with this kernel.
        name: kernel name in the program.
    """

    def __init__(self, program, name):
        super(Kernel, self).__init__()
        self._program = program
        self._name = name
        err = cl.ffi.new("cl_int *")
        ss = cl.ffi.new("char[]", name.encode("utf-8"))
        self._handle = self._lib.clCreateKernel(program.handle, ss, err)
        if err[0]:
            self._handle = None
            raise CLRuntimeError("clCreateKernel() failed with error %s" %
                                 CL.get_error_description(err[0]),
                                 err[0])

    @property
    def program(self):
        """
        Program object associated with this kernel.
        """
        return self._program

    @property
    def name(self):
        """
        kernel name in the program.
        """
        return self._name

    @property
    def reference_count(self):
        buf = cl.ffi.new("cl_uint *")
        self._get_kernel_info(cl.CL_KERNEL_REFERENCE_COUNT, buf)
        return buf[0]

    @property
    def num_args(self):
        buf = cl.ffi.new("size_t *")
        self._get_kernel_info(cl.CL_KERNEL_NUM_ARGS, buf)
        return buf[0]

    @property
    def attributes(self):
        buf = cl.ffi.new("char[]", 4096)
        self._get_kernel_info(cl.CL_KERNEL_ATTRIBUTES, buf)
        return cl.ffi.string(buf).decode("utf-8", "replace").strip()

    def set_arg(self, idx, vle, size=None):
        """Sets kernel argument.

        Parameters:
            idx: index of the kernel argument (zero-based).
            vle: kernel argument:
                 - for buffers should be an instance of Buffer,
                 - for scalars should be a numpy array slice
                   (k[0:1] for example),
                 - for NULL should be None,
                 - may be cffi pointer also, in such case size should be set.
            size: size of the vle (may be None for buffers and scalars).
        """
        if isinstance(vle, Buffer):
            arg_value = cl.ffi.new("cl_mem[]", 1)
            arg_value[0] = vle.handle
            arg_size = cl.ffi.sizeof("cl_mem")
        elif hasattr(vle, "__array_interface__"):
            arg_value = cl.ffi.cast("const void*",
                                    vle.__array_interface__["data"][0])
            arg_size = vle.nbytes if size is None else size
        elif vle is None:
            arg_value = cl.NULL
            arg_size = 0
        elif type(vle) == type(cl.NULL):  # cffi pointer
            arg_value = cl.ffi.cast("const void*", vle)
            if size is None:
                raise ValueError("size should be set in case of cffi pointer")
            arg_size = size
        else:
            raise ValueError("vle should be of type Buffer, "
                             "numpy array, cffi pointer or None "
                             "in Kernel::set_arg()")
        n = self._lib.clSetKernelArg(self.handle, idx, arg_size, arg_value)
        if n:
            raise CLRuntimeError("clSetKernelArg(%d, %s) failed with error "
                                 "%s" % (idx, repr(vle),
                                         CL.get_error_description(n)),
                                 n)

    def set_args(self, *args):
        skip_until = 0
        for i, arg in enumerate(args):
            if arg is skip:
                continue
            if isinstance(arg, skip):
                skip_until = i + arg.number
            if i < skip_until:
                continue
            if isinstance(arg, tuple) and len(arg) == 2:
                self.set_arg(i, *arg)
            else:
                self.set_arg(i, arg)

    def release(self):
        if self.handle is not None:
            self._lib.clReleaseKernel(self.handle)
            self._handle = None

    def _get_kernel_info(self, code, buf):
        sz = cl.ffi.new("size_t *")
        err = self._lib.clGetKernelInfo(self.handle, code,
                                        cl.ffi.sizeof(buf), buf, sz)
        if err:
            raise CLRuntimeError("clGetKernelInfo() failed with error %s" %
                                 CL.get_error_description(err), err)
        return sz[0]

    def __del__(self):
        self.release()


class Program(CL):
    """Holds OpenCL program.

    Attributes:
        context: Context object associated with this program.
        devices: list of Device objects associated with this program.
        build_logs: list of program build logs (same length as devices list).
        src: program source.
        include_dirs: list of include dirs.
        options: additional build options.
        binary: False if the program should be created from source; otherwise,
                src is interpreted as precompiled binaries iterable.
    """

    def __init__(self, context, devices, src, include_dirs=(), options="",
                 binary=False):
        super(Program, self).__init__()
        self._context = context
        self._devices = devices
        self._src = src.encode("utf-8") if not binary else None
        self._include_dirs = list(include_dirs)
        self._options = options.strip().encode("utf-8")
        self._build_logs = []
        if not binary:
            self._create_program_from_source()
        else:
            self._create_program_from_binary(src)

    @property
    def context(self):
        """
        Context object associated with this program.
        """
        return self._context

    @property
    def devices(self):
        """
        List of Device objects associated with this program.
        """
        return self._devices

    @property
    def build_logs(self):
        """
        List of program build logs (same length as devices list).
        """
        return self._build_logs

    @property
    def source(self):
        """
        Program source.
        """
        return self._src

    @property
    def include_dirs(self):
        """
        List of include dirs.
        """
        return self._include_dirs

    @property
    def options(self):
        """
        Additional build options.
        """
        return self._options

    @property
    def reference_count(self):
        buf = cl.ffi.new("cl_uint *")
        self._get_program_info(cl.CL_PROGRAM_REFERENCE_COUNT, buf)
        return buf[0]

    @property
    def num_kernels(self):
        buf = cl.ffi.new("size_t *")
        self._get_program_info(cl.CL_PROGRAM_NUM_KERNELS, buf)
        return buf[0]

    @property
    def kernel_names(self):
        buf = cl.ffi.new("char[]", 4096)
        self._get_program_info(cl.CL_PROGRAM_KERNEL_NAMES, buf)
        names = cl.ffi.string(buf).decode("utf-8", "replace")
        return names.split(';')

    @property
    def binaries(self):
        sizes = cl.ffi.new("size_t[]", len(self.devices))
        self._get_program_info(cl.CL_PROGRAM_BINARY_SIZES, sizes)
        buf = cl.ffi.new("char *[]", len(self.devices))
        bufr = []  # to hold the references to cffi arrays
        for i in range(len(self.devices)):
            bufr.append(cl.ffi.new("char[]", sizes[i]))
            buf[i] = bufr[-1]
        self._get_program_info(cl.CL_PROGRAM_BINARIES, buf)
        bins = []
        for i in range(len(self.devices)):
            bins.append(bytes(cl.ffi.buffer(buf[i], sizes[i])[0:sizes[i]]))
        del bufr
        return bins

    def get_kernel(self, name):
        """Returns Kernel object from its name.
        """
        return Kernel(self, name)

    def _get_program_info(self, code, buf):
        sz = cl.ffi.new("size_t *")
        err = self._lib.clGetProgramInfo(self.handle, code,
                                         cl.ffi.sizeof(buf), buf, sz)
        if err:
            raise CLRuntimeError("clGetProgramInfo() failed with error %s" %
                                 CL.get_error_description(err), err)
        return sz[0]

    def _get_build_logs(self, device_list):
        del self.build_logs[:]
        log = cl.ffi.new("char[]", 65536)
        sz = cl.ffi.new("size_t *")
        for dev in device_list:
            e = self._lib.clGetProgramBuildInfo(
                self.handle, dev, cl.CL_PROGRAM_BUILD_LOG, cl.ffi.sizeof(log),
                log, sz)
            if e or sz[0] <= 0:
                self.build_logs.append("")
                continue
            self.build_logs.append(cl.ffi.string(log).decode("utf-8",
                                                             "replace"))

    def _create_program_from_source(self):
        err = cl.ffi.new("cl_int *")
        srcptr = cl.ffi.new("char[]", self.source)
        strings = cl.ffi.new("char*[]", 1)
        strings[0] = srcptr
        self._handle = self._lib.clCreateProgramWithSource(
            self.context.handle, 1, strings, cl.NULL, err)
        del srcptr
        if err[0]:
            self._handle = None
            raise CLRuntimeError("clCreateProgramWithSource() failed with "
                                 "error %s" %
                                 CL.get_error_description(err[0]), err[0])
        options = self.options.decode("utf-8")
        for dirnme in self.include_dirs:
            if not len(dirnme):
                continue
            options += " -I " + (dirnme if dirnme.find(" ") < 0
                                 else "\'%s\'" % dirnme)
        options = options.encode("utf-8")
        n_devices = len(self.devices)
        device_list = cl.ffi.new("cl_device_id[]", n_devices)
        for i, dev in enumerate(self.devices):
            device_list[i] = dev.handle
        err = self._lib.clBuildProgram(self.handle, n_devices, device_list,
                                       options, cl.NULL, cl.NULL)
        del options
        self._get_build_logs(device_list)
        if err:
            raise CLRuntimeError(
                "clBuildProgram() failed with error %s\n"
                "Logs are:\n%s\nSource was:\n%s\n" %
                (CL.get_error_description(err), "\n".join(self.build_logs),
                 self.source),
                err)

    def _create_program_from_binary(self, src):
        count = len(self.devices)
        if count != len(src):
            raise ValueError("You have supplied %d binaries for %d devices" %
                             (len(src), count))
        device_list = cl.ffi.new("cl_device_id[]", count)
        for i, dev in enumerate(self.devices):
            device_list[i] = dev.handle
        lengths = cl.ffi.new("size_t[]", count)
        for i, b in enumerate(src):
            lengths[i] = len(b)
        binaries_ffi = cl.ffi.new("unsigned char *[]", count)
        binaries_ref = []  # this is to prevent Python from garbage collecting
                           # binaries_ffi[:]
        for i, b in enumerate(src):
            binaries_ref.append(cl.ffi.new("unsigned char[]", b))
            binaries_ffi[i] = binaries_ref[-1]
        binary_status = cl.ffi.new("cl_int[]", count)
        err = cl.ffi.new("cl_int *")
        self._handle = self._lib.clCreateProgramWithBinary(
            self.context.handle, count, device_list, lengths,
            binaries_ffi, binary_status, err)
        if err[0]:
            self._handle = None
            statuses = [CL.get_error_name_from_code(s) for s in binary_status]
            raise CLRuntimeError("clCreateProgramWithBinary() failed with "
                                 "error %s; status %s" % (
                                     CL.get_error_description(err[0]),
                                     ", ".join(statuses)),
                                 err[0])
        err = self._lib.clBuildProgram(self.handle, count, device_list,
                                       self.options, cl.NULL, cl.NULL)
        del binaries_ref
        self._get_build_logs(device_list)
        if err:
            raise CLRuntimeError("clBuildProgram() failed with error %s.\n"
                                 "Logs are:\n%s" % (
                                     CL.get_error_description(err),
                                     "\n".join(self.build_logs)),
                                 err)

    def release(self):
        if self.handle is not None:
            self._lib.clReleaseProgram(self.handle)
            self._handle = None

    def __del__(self):
        self.release()


class Context(CL):
    """Holds OpenCL context.

    Attributes:
        platform: Platform object associated with this context.
        devices: list of Device object associated with this context.
    """
    def __init__(self, platform, devices):
        super(Context, self).__init__()
        self._platform = platform
        self._devices = devices
        props = cl.ffi.new("cl_context_properties[]", 3)
        props[0] = cl.CL_CONTEXT_PLATFORM
        props[1] = cl.ffi.cast("cl_context_properties", platform.handle)
        props[2] = 0
        err = cl.ffi.new("cl_int *")
        n_devices = len(devices)
        device_list = cl.ffi.new("cl_device_id[]", n_devices)
        for i, dev in enumerate(devices):
            device_list[i] = dev.handle
        self._handle = self._lib.clCreateContext(
            props, n_devices, device_list, cl.NULL, cl.NULL, err)
        if err[0]:
            self._handle = None
            raise CLRuntimeError("clCreateContext() failed with error %s" %
                                 CL.get_error_description(err[0]),
                                 err[0])

    @property
    def platform(self):
        """
        Platform object associated with this context.
        """
        return self._platform

    @property
    def devices(self):
        """
        List of Device object associated with this context.
        """
        return self._devices

    def create_queue(self, device, flags=0):
        """Creates Queue object for the supplied device.

        Parameters:
            device: Device object.
            flags: queue flags (for example
                                CL_QUEUE_OUT_OF_ORDER_EXEC_MODE_ENABLE).

        Returns:
            Queue object.
        """
        return Queue(self, device, flags)

    def create_buffer(self, flags, host_array=None, size=None):
        """Creates Buffer object based on host_array.

        Parameters:
            host_array: numpy array of None.
            size: size if host_array is not a numpy array.

        Returns:
            Buffer object.
        """
        return Buffer(self, flags, host_array, size)

    def create_program(self, src, include_dirs=(), options="", devices=None,
                       binary=False):
        """Creates and builds OpenCL program from source
           for the supplied devices associated with this context.

        Parameters:
            src: program source.
            include_dirs: list of include directories.
            options: additional build options.
            devices: list of devices on which to build the program
                     (if None will build on all devices).
        Returns:
            Program object.
        """
        return Program(self, self.devices if devices is None else devices,
                       src, include_dirs, options, binary)

    def release(self):
        if self.handle is not None:
            self._lib.clReleaseContext(self.handle)
            self._handle = None

    def __del__(self):
        self.release()


class Device(CL):
    """OpenCL device.

    Attributes:
        platform: Platform object associated with this device.
        type: OpenCL type of the device (integer).
        name: OpenCL name of the device.
        path: opencl4py device identifier,
        version: OpenCL version number of the device (float).
        version_string: OpenCL version string of the device.
        vendor: OpenCL vendor name of the device.
        vendor_id: OpenCL vendor id of the device (integer).
        memsize: global memory size of the device.
        memalign: align in bytes, required for clMapBuffer.
    """
    def __init__(self, handle, platform, path):
        super(Device, self).__init__()
        self._handle = handle
        self._platform = platform
        self._path = path

        self._version_string = self._get_device_info_str(
            cl.CL_DEVICE_OPENCL_C_VERSION)
        n = len("OpenCL C ")
        m = self._version_string.find(" ", n)
        try:
            self._version = float(self._version_string[n:m])
        except ValueError:
            self._version = 0.0

    @property
    def platform(self):
        """
        Platform object associated with this device.
        """
        return self._platform

    @property
    def type(self):
        """
        OpenCL type of the device (integer).
        """
        return self._get_device_info_int(cl.CL_DEVICE_TYPE)

    @property
    def name(self):
        """
        OpenCL name of the device.
        """
        return self._get_device_info_str(cl.CL_DEVICE_NAME)

    @property
    def path(self):
        """
        opencl4py device identifier,
        """
        return self._path

    @property
    def version(self):
        """
        OpenCL version number of the device (float).
        """
        return self._version

    @property
    def version_string(self):
        """
        OpenCL version string of the device.
        """
        return self._version_string

    @property
    def vendor(self):
        """
        OpenCL vendor name of the device.
        """
        return self._get_device_info_str(cl.CL_DEVICE_VENDOR)

    @property
    def vendor_id(self):
        """
        OpenCL vendor id of the device (integer).
        """
        return self._get_device_info_int(cl.CL_DEVICE_VENDOR_ID)

    @property
    def memsize(self):
        """
        Global memory size of the device.
        """
        return self.global_memsize

    @property
    def memalign(self):
        """
        Alignment in bytes, required by clMapBuffer.
        """
        return self.mem_base_addr_align

    @property
    def available(self):
        return self._get_device_info_bool(cl.CL_DEVICE_AVAILABLE)

    @property
    def compiler_available(self):
        return self._get_device_info_bool(cl.CL_DEVICE_COMPILER_AVAILABLE)

    @property
    def little_endian(self):
        return self._get_device_info_bool(cl.CL_DEVICE_ENDIAN_LITTLE)

    @property
    def supports_error_correction(self):
        return self._get_device_info_bool(
            cl.CL_DEVICE_ERROR_CORRECTION_SUPPORT)

    @property
    def host_unified_memory(self):
        return self._get_device_info_bool(cl.CL_DEVICE_HOST_UNIFIED_MEMORY)

    @property
    def supports_images(self):
        return self._get_device_info_bool(cl.CL_DEVICE_IMAGE_SUPPORT)

    @property
    def linker_available(self):
        return self._get_device_info_bool(cl.CL_DEVICE_LINKER_AVAILABLE)

    @property
    def prefers_user_sync(self):
        return self._get_device_info_bool(
            cl.CL_DEVICE_PREFERRED_INTEROP_USER_SYNC)

    @property
    def address_bits(self):
        return self._get_device_info_int(cl.CL_DEVICE_ADDRESS_BITS)

    @property
    def double_fp_config(self):
        return self._get_device_info_int(cl.CL_DEVICE_DOUBLE_FP_CONFIG)

    @property
    def execution_capabilities(self):
        return self._get_device_info_int(cl.CL_DEVICE_EXECUTION_CAPABILITIES)

    @property
    def global_mem_cache_size(self):
        return self._get_device_info_int(cl.CL_DEVICE_GLOBAL_MEM_CACHE_SIZE)

    @property
    def global_mem_cache_line_size(self):
        return self._get_device_info_int(
            cl.CL_DEVICE_GLOBAL_MEM_CACHELINE_SIZE)

    @property
    def half_fp_config(self):
        return self._get_device_info_int(cl.CL_DEVICE_HALF_FP_CONFIG)

    @property
    def image2d_max_height(self):
        return self._get_device_info_int(cl.CL_DEVICE_IMAGE2D_MAX_HEIGHT)

    @property
    def image2d_max_width(self):
        return self._get_device_info_int(cl.CL_DEVICE_IMAGE2D_MAX_WIDTH)

    @property
    def image3d_max_depth(self):
        return self._get_device_info_int(cl.CL_DEVICE_IMAGE3D_MAX_DEPTH)

    @property
    def image3d_max_height(self):
        return self._get_device_info_int(cl.CL_DEVICE_IMAGE3D_MAX_HEIGHT)

    @property
    def image3d_max_width(self):
        return self._get_device_info_int(cl.CL_DEVICE_IMAGE3D_MAX_WIDTH)

    @property
    def image_max_buffer_size(self):
        return self._get_device_info_int(cl.CL_DEVICE_IMAGE_MAX_BUFFER_SIZE)

    @property
    def image_max_array_size(self):
        return self._get_device_info_int(cl.CL_DEVICE_IMAGE_MAX_ARRAY_SIZE)

    @property
    def local_memsize(self):
        return self._get_device_info_int(cl.CL_DEVICE_LOCAL_MEM_SIZE)

    @property
    def global_memsize(self):
        return self._get_device_info_int(cl.CL_DEVICE_GLOBAL_MEM_SIZE)

    @property
    def max_clock_frequency(self):
        return self._get_device_info_int(cl.CL_DEVICE_MAX_CLOCK_FREQUENCY)

    @property
    def max_compute_units(self):
        return self._get_device_info_int(cl.CL_DEVICE_MAX_COMPUTE_UNITS)

    @property
    def max_constant_args(self):
        return self._get_device_info_int(cl.CL_DEVICE_MAX_CONSTANT_ARGS)

    @property
    def max_constant_buffer_size(self):
        return self._get_device_info_int(
            cl.CL_DEVICE_MAX_CONSTANT_BUFFER_SIZE)

    @property
    def max_mem_alloc_size(self):
        return self._get_device_info_int(cl.CL_DEVICE_MAX_MEM_ALLOC_SIZE)

    @property
    def max_parameter_size(self):
        return self._get_device_info_int(cl.CL_DEVICE_MAX_PARAMETER_SIZE)

    @property
    def max_read_image_args(self):
        return self._get_device_info_int(cl.CL_DEVICE_MAX_READ_IMAGE_ARGS)

    @property
    def max_work_group_size(self):
        return self._get_device_info_int(cl.CL_DEVICE_MAX_WORK_GROUP_SIZE)

    @property
    def max_work_item_dimensions(self):
        return self._get_device_info_int(
            cl.CL_DEVICE_MAX_WORK_ITEM_DIMENSIONS)

    @property
    def max_write_image_args(self):
        return self._get_device_info_int(cl.CL_DEVICE_MAX_WRITE_IMAGE_ARGS)

    @property
    def mem_base_addr_align(self):
        return self._get_device_info_int(cl.CL_DEVICE_MEM_BASE_ADDR_ALIGN)

    @property
    def min_data_type_align_size(self):
        return self._get_device_info_int(
            cl.CL_DEVICE_MIN_DATA_TYPE_ALIGN_SIZE)

    @property
    def preferred_vector_width_char(self):
        return self._get_device_info_int(
            cl.CL_DEVICE_PREFERRED_VECTOR_WIDTH_CHAR)

    @property
    def preferred_vector_width_short(self):
        return self._get_device_info_int(
            cl.CL_DEVICE_PREFERRED_VECTOR_WIDTH_SHORT)

    @property
    def preferred_vector_width_int(self):
        return self._get_device_info_int(
            cl.CL_DEVICE_PREFERRED_VECTOR_WIDTH_INT)

    @property
    def preferred_vector_width_long(self):
        return self._get_device_info_int(
            cl.CL_DEVICE_PREFERRED_VECTOR_WIDTH_LONG)

    @property
    def preferred_vector_width_float(self):
        return self._get_device_info_int(
            cl.CL_DEVICE_PREFERRED_VECTOR_WIDTH_FLOAT)

    @property
    def preferred_vector_width_double(self):
        return self._get_device_info_int(
            cl.CL_DEVICE_PREFERRED_VECTOR_WIDTH_DOUBLE)

    @property
    def preferred_vector_width_half(self):
        return self._get_device_info_int(
            cl.CL_DEVICE_PREFERRED_VECTOR_WIDTH_HALF)

    @property
    def printf_buffer_size(self):
        return self._get_device_info_int(cl.CL_DEVICE_PRINTF_BUFFER_SIZE)

    @property
    def profiling_timer_resolution(self):
        return self._get_device_info_int(
            cl.CL_DEVICE_PROFILING_TIMER_RESOLUTION)

    @property
    def reference_count(self):
        return self._get_device_info_int(cl.CL_DEVICE_REFERENCE_COUNT)

    @property
    def single_fp_config(self):
        return self._get_device_info_int(cl.CL_DEVICE_SINGLE_FP_CONFIG)

    @property
    def built_in_kernels(self):
        return [kernel.strip() for kernel in self._get_device_info_str(
            cl.CL_DEVICE_BUILT_IN_KERNELS).split(';')
            if kernel.strip()]

    @property
    def extensions(self):
        return [ext.strip() for ext in self._get_device_info_str(
            cl.CL_DEVICE_EXTENSIONS).split(' ')
            if ext.strip()]

    @property
    def profile(self):
        return self._get_device_info_str(cl.CL_DEVICE_PROFILE)

    @property
    def driver_version(self):
        return self._get_device_info_str(cl.CL_DRIVER_VERSION)

    @property
    def max_work_item_sizes(self):
        value = cl.ffi.new("size_t[]", self.max_work_item_dimensions)
        err = self._lib.clGetDeviceInfo(
            self._handle, cl.CL_DEVICE_MAX_WORK_ITEM_SIZES,
            cl.ffi.sizeof(value), value, cl.NULL)
        if err:
            return None
        return list(value)

    def _get_device_info_bool(self, name):
        value = cl.ffi.new("cl_bool[]", 1)
        err = self._lib.clGetDeviceInfo(self._handle, name,
                                        cl.ffi.sizeof(value), value, cl.NULL)
        if err:
            raise CLRuntimeError("clGetDeviceInfo(%d) failed with error %s" %
                                 (name, CL.get_error_description(err)), err)
        return bool(value[0])

    def _get_device_info_int(self, name):
        value = cl.ffi.new("uint64_t[]", 1)
        err = self._lib.clGetDeviceInfo(self._handle, name,
                                        cl.ffi.sizeof(value), value, cl.NULL)
        if err:
            raise CLRuntimeError("clGetDeviceInfo(%d) failed with error %s" %
                                 (name, CL.get_error_description(err)), err)
        return int(value[0])

    def _get_device_info_str(self, name):
        value = cl.ffi.new("char[]", 1024)
        err = self._lib.clGetDeviceInfo(self._handle, name,
                                        cl.ffi.sizeof(value), value, cl.NULL)
        if err:
            raise CLRuntimeError("clGetDeviceInfo(%d) failed with error %s" %
                                 (name, CL.get_error_description(err)), err)
        return cl.ffi.string(value).decode("utf-8")


class Platform(CL):
    """OpenCL platform.

    Attributes:
        devices: list of Device objects available on this platform.
        name: OpenCL name of the platform.
        path: opencl4py platform identifier.
    """
    def __init__(self, handle, path):
        super(Platform, self).__init__()
        self._handle = handle
        self._path = path

        sz = cl.ffi.new("size_t[]", 1)
        nme = cl.ffi.new("char[]", 256)
        n = self._lib.clGetPlatformInfo(handle, cl.CL_PLATFORM_NAME,
                                        256, nme, sz)
        self._name = ((b"".join(nme[0:sz[0] - 1])).decode("utf-8")
                      if not n else None)

        nn = cl.ffi.new("cl_uint[]", 1)
        n = self._lib.clGetDeviceIDs(handle, cl.CL_DEVICE_TYPE_ALL,
                                     0, cl.NULL, nn)
        if n:
            raise CLRuntimeError("clGetDeviceIDs() failed with error %s" %
                                 CL.get_error_description(n), n)
        ids = cl.ffi.new("cl_device_id[]", nn[0])
        n = self._lib.clGetDeviceIDs(handle, cl.CL_DEVICE_TYPE_ALL,
                                     nn[0], ids, nn)
        if n:
            raise CLRuntimeError("clGetDeviceIDs() failed with error %s" %
                                 CL.get_error_description(n), n)
        self._devices = list(Device(dev_id, self,
                                    "%s:%d" % (self.path, dev_num))
                             for dev_id, dev_num in zip(ids, range(len(ids))))

    @property
    def devices(self):
        """
        List of Device objects available on this platform.
        """
        return self._devices

    @property
    def name(self):
        """
        OpenCL name of the platform.
        """
        return self._name

    @property
    def path(self):
        """
        opencl4py platform identifier.
        """
        return self._path

    def __iter__(self):
        return iter(self.devices)

    def create_context(self, devices):
        """Creates OpenCL context on this platform and selected devices.

        Parameters:
            devices: list of Device objects.

        Returns:
            Context object.
        """
        return Context(self, devices)


class Platforms(CL):
    """List of OpenCL plaforms.

    Attributes:
        platforms: list of Platform objects.
    """
    def __init__(self):
        cl.initialize()
        super(Platforms, self).__init__()
        nn = cl.ffi.new("cl_uint[]", 1)
        n = self._lib.clGetPlatformIDs(0, cl.NULL, nn)
        if n:
            raise CLRuntimeError("clGetPlatformIDs() failed with error %s" %
                                 CL.get_error_description(n), n)
        ids = cl.ffi.new("cl_platform_id[]", nn[0])
        n = self._lib.clGetPlatformIDs(nn[0], ids, nn)
        if n:
            raise CLRuntimeError("clGetPlatformIDs() failed with error %s" %
                                 CL.get_error_description(n), n)
        self._platforms = list(Platform(p_id, str(p_num))
                               for p_id, p_num in zip(ids, range(len(ids))))

    @property
    def platforms(self):
        return self._platforms

    def __iter__(self):
        return iter(self.platforms)

    def dump_devices(self):
        """Returns string with information about OpenCL platforms and devices.
        """
        if not len(self.platforms):
            return "No OpenCL devices available."
        lines = []
        for i, platform in enumerate(self.platforms):
            lines.append("Platform %d: %s" % (i, platform.name.strip()))
            for j, device in enumerate(platform.devices):
                lines.append("\tDevice %d: %s (%d Mb, %d align, %s)" % (
                    j, device.name.strip(), device.memsize // (1024 * 1024),
                    device.memalign, device.version_string.strip()))
        return "\n".join(lines)

    def create_some_context(self):
        """Returns Context object with some OpenCL platform, devices attached.

        If environment variable PYOPENCL_CTX is set and not empty,
        gets context based on it, format is:
        <platform number>:<comma separated device numbers>
        (Examples: 0:0 - first platform, first device,
                   1:0,2 - second platform, first and third devices).

        If PYOPENCL_CTX is not set and os.isatty(0) == True, then
        displays available devices and reads line from stdin in the same
        format as PYOPENCL_CTX.

        Else chooses first platform and device.
        """
        if len(self.platforms) == 1 and len(self.platforms[0].devices) == 1:
            return self.platforms[0].create_context(self.platforms[0].devices)
        import os
        ctx = os.environ.get("PYOPENCL_CTX")
        if ctx is None or not len(ctx):
            if os.isatty(0):
                import sys
                sys.stdout.write(
                    "\nEnter "
                    "<platform number>:<comma separated device numbers> or "
                    "set PYOPENCL_CTX environment variable.\n"
                    "Examples: 0:0 - first platform, first device;\n"
                    "          1:0,2 - second platform, first and third "
                    "devices.\n"
                    "\nOpenCL devices available:\n\n%s\n\n" %
                    (self.dump_devices()))
                sys.stdout.flush()
                ctx = sys.stdin.readline().strip()
            else:
                ctx = ""
        idx = ctx.find(":")
        if idx >= 0:
            try:
                platform_number = int(ctx[:idx]) if len(ctx[:idx]) else 0
            except ValueError:
                raise ValueError("Incorrect platform number")
            ctx = ctx[idx + 1:]
        else:
            platform_number = 0
        device_strings = ctx.split(",")
        device_numbers = []
        try:
            for s in device_strings:
                device_numbers.append(int(s) if len(s) else 0)
        except ValueError:
            raise ValueError("Incorrect device number")
        try:
            platform = self.platforms[platform_number]
        except IndexError:
            raise IndexError("Platform index is out of range")
        devices = []
        try:
            for i in device_numbers:
                devices.append(platform.devices[i])
        except IndexError:
            raise IndexError("Devicve index is out of range")
        return platform.create_context(devices)
