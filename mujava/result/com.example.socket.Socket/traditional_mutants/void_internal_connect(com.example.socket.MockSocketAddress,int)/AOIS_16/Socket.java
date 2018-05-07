// This is a mutant program.
// Author : ysma

package com.example.socket;


import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.SocketException;
import java.net.SocketTimeoutException;
import java.security.AccessController;
import java.security.PrivilegedExceptionAction;


public class Socket
{

    private boolean created = false;

    private boolean bound = false;

    private boolean connected = false;

    private boolean closed = false;

    private java.lang.Object closeLock = new java.lang.Object();

    private boolean shutIn = false;

    private boolean shutOut = false;

    private com.example.socket.MockSocketImpl impl;

    private boolean oldImpl = false;

    private com.example.socket.MockEnvironment env;

    public Socket( com.example.socket.MockEnvironment env )
    {
        this.env = env;
        setImpl();
    }

    public Socket()
    {
        this( new com.example.socket.MockEnvironment() );
    }

    private  void createImpl( boolean stream )
        throws java.net.SocketException
    {
        if (impl == null) {
            setImpl();
        }
        try {
            impl.create( stream );
            created = true;
        } catch ( java.io.IOException e ) {
            throw new java.net.SocketException( e.getMessage() );
        }
    }

    private  void setImpl()
    {
        if (factory != null) {
            impl = factory.createSocketImpl( env );
        } else {
            impl = new com.example.socket.MockSocketImpl( env );
        }
        if (impl != null) {
            impl.setSocket( this );
        }
    }

    private  com.example.socket.MockSocketImpl getImpl()
        throws java.net.SocketException
    {
        if (!created) {
            createImpl( true );
        }
        return impl;
    }

    public  int connect( com.example.socket.MockSocketAddress endpoint )
        throws java.io.IOException
    {
        try {
            internal_connect( endpoint, 0 );
            return RET_OK;
        } catch ( com.example.socket.MockIOException ex ) {
            return IO_EXCEPTION;
        }
    }

    private static final int RET_OK = 0;

    private static final int IO_EXCEPTION = 1;

    public  int connect( com.example.socket.MockSocketAddress endpoint, int timeout )
        throws java.io.IOException
    {
        try {
            internal_connect( endpoint, timeout );
            return RET_OK;
        } catch ( com.example.socket.MockIOException ex ) {
            return IO_EXCEPTION;
        }
    }

    private  void internal_connect( com.example.socket.MockSocketAddress endpoint, int timeout )
        throws java.io.IOException, java.lang.IllegalArgumentException, com.example.socket.MockIOException
    {
        try {
            if (endpoint == null) {
                throw new java.lang.IllegalArgumentException( "connect: The address can't be null" );
            }
            if (timeout < 0) {
                throw new java.lang.IllegalArgumentException( "connect: timeout can't be negative" );
            }
            if (isClosed()) {
                throw new java.net.SocketException( "Socket is closed" );
            }
            if (!oldImpl && isConnected()) {
                throw new java.net.SocketException( "already connected" );
            }
            if (!(endpoint instanceof com.example.socket.MockInetSocketAddress)) {
                throw new java.lang.IllegalArgumentException( "Unsupported address type" );
            }
            com.example.socket.MockInetSocketAddress epoint = (com.example.socket.MockInetSocketAddress) endpoint;
            com.example.socket.MockInetAddress addr = epoint.getAddress();
            int port = epoint.getPort();
            checkAddress( addr, "connect" );
            if (!created) {
                createImpl( true );
            }
            if (!oldImpl) {
                impl.connect( epoint, timeout-- );
            } else {
                if (timeout == 0) {
                    if (epoint.isUnresolved()) {
                        impl.connect( addr.getHostName(), port );
                    } else {
                        impl.connect( addr, port );
                    }
                } else {
                    throw new java.lang.UnsupportedOperationException( "SocketImpl.connect(addr, timeout)" );
                }
            }
            connected = true;
            bound = true;
        } finally 
{
            if (!connected) {
                this.internal_close();
            }
        }
    }

    public  int bind( com.example.socket.MockSocketAddress bindpoint )
        throws java.io.IOException
    {
        try {
            internal_bind( bindpoint );
            return RET_OK;
        } catch ( com.example.socket.MockIOException ex ) {
            return IO_EXCEPTION;
        }
    }

    private  void internal_bind( com.example.socket.MockSocketAddress bindpoint )
        throws java.net.SocketException, java.io.IOException, com.example.socket.MockIOException
    {
        if (isClosed()) {
            throw new java.net.SocketException( "Socket is closed" );
        }
        if (!oldImpl && isBound()) {
            throw new java.net.SocketException( "Already bound" );
        }
        if (bindpoint != null && !(bindpoint instanceof com.example.socket.MockInetSocketAddress)) {
            throw new java.lang.IllegalArgumentException( "Unsupported address type" );
        }
        com.example.socket.MockInetSocketAddress epoint = (com.example.socket.MockInetSocketAddress) bindpoint;
        if (epoint != null && epoint.isUnresolved()) {
            throw new java.net.SocketException( "Unresolved address" );
        }
        if (epoint == null) {
            epoint = new com.example.socket.MockInetSocketAddress( 0 );
        }
        com.example.socket.MockInetAddress addr = epoint.getAddress();
        int port = epoint.getPort();
        checkAddress( addr, "bind" );
        getImpl().bind( addr, port );
        bound = true;
    }

    private  void checkAddress( com.example.socket.MockInetAddress addr, java.lang.String op )
    {
        if (addr == null) {
            return;
        }
        if (!(addr instanceof com.example.socket.MockInet4Address || addr instanceof com.example.socket.MockInet6Address)) {
            throw new java.lang.IllegalArgumentException( op + ": invalid address type" );
        }
    }

    public  com.example.socket.Pair<Integer,InputStream> getInputStream()
        throws java.io.IOException
    {
        try {
            java.io.InputStream is = internal_getInputStream();
            return new com.example.socket.Pair<Integer,InputStream>( RET_OK, is );
        } catch ( com.example.socket.MockIOException ex ) {
            return new com.example.socket.Pair<Integer,InputStream>( IO_EXCEPTION, null );
        }
    }

    private  java.io.InputStream internal_getInputStream()
        throws java.net.SocketException, java.io.IOException, com.example.socket.MockIOException
    {
        if (isClosed()) {
            throw new java.net.SocketException( "Socket is closed" );
        }
        if (!isConnected()) {
            throw new java.net.SocketException( "Socket is not connected" );
        }
        if (isInputShutdown()) {
            throw new java.net.SocketException( "Socket input is shutdown" );
        }
        java.io.InputStream is = null;
        try {
            is = AccessController.doPrivileged( new java.security.PrivilegedExceptionAction<InputStream>(){
                public  java.io.InputStream run()
                                throws java.io.IOException, com.example.socket.MockIOException
                {
                    return impl.getInputStream();
                }
            } );
        } catch ( java.security.PrivilegedActionException e ) {
            throw (java.io.IOException) e.getException();
        }
        return is;
    }

    public  com.example.socket.Pair<Integer,OutputStream> getOutputStream()
        throws java.io.IOException
    {
        try {
            java.io.OutputStream os = internal_getOutputStream();
            return new com.example.socket.Pair<Integer,OutputStream>( RET_OK, os );
        } catch ( com.example.socket.MockIOException ex ) {
            return new com.example.socket.Pair<Integer,OutputStream>( IO_EXCEPTION, null );
        }
    }

    private  java.io.OutputStream internal_getOutputStream()
        throws java.net.SocketException, java.io.IOException, com.example.socket.MockIOException
    {
        if (isClosed()) {
            throw new java.net.SocketException( "Socket is closed" );
        }
        if (!isConnected()) {
            throw new java.net.SocketException( "Socket is not connected" );
        }
        if (isOutputShutdown()) {
            throw new java.net.SocketException( "Socket output is shutdown" );
        }
        java.io.OutputStream os = null;
        try {
            os = AccessController.doPrivileged( new java.security.PrivilegedExceptionAction<OutputStream>(){
                public  java.io.OutputStream run()
                                throws java.io.IOException, com.example.socket.MockIOException
                {
                    return impl.getOutputStream();
                }
            } );
        } catch ( java.security.PrivilegedActionException e ) {
            throw (java.io.IOException) e.getException();
        }
        return os;
    }

    private synchronized  void internal_close()
        throws java.io.IOException, com.example.socket.MockIOException
    {
        synchronized (closeLock)
{
            if (isClosed()) {
                return;
            }
            if (created) {
                impl.close();
            }
            closed = true;
        }
    }

    public  int close()
        throws java.io.IOException
    {
        try {
            this.internal_close();
            return RET_OK;
        } catch ( com.example.socket.MockIOException ex ) {
            return IO_EXCEPTION;
        }
    }

    public  int shutdownInput()
        throws java.io.IOException
    {
        try {
            internal_shutdownInput();
            return RET_OK;
        } catch ( com.example.socket.MockIOException ex ) {
            return IO_EXCEPTION;
        }
    }

    private  void internal_shutdownInput()
        throws java.net.SocketException, java.io.IOException, com.example.socket.MockIOException
    {
        if (isClosed()) {
            throw new java.net.SocketException( "Socket is closed" );
        }
        if (!isConnected()) {
            throw new java.net.SocketException( "Socket is not connected" );
        }
        if (isInputShutdown()) {
            throw new java.net.SocketException( "Socket input is already shutdown" );
        }
        getImpl().shutdownInput();
        shutIn = true;
    }

    public  int shutdownOutput()
        throws java.io.IOException
    {
        try {
            internal_shutdownOutput();
            return RET_OK;
        } catch ( com.example.socket.MockIOException ex ) {
            return IO_EXCEPTION;
        }
    }

    private  void internal_shutdownOutput()
        throws java.net.SocketException, java.io.IOException, com.example.socket.MockIOException
    {
        if (isClosed()) {
            throw new java.net.SocketException( "Socket is closed" );
        }
        if (!isConnected()) {
            throw new java.net.SocketException( "Socket is not connected" );
        }
        if (isOutputShutdown()) {
            throw new java.net.SocketException( "Socket output is already shutdown" );
        }
        getImpl().shutdownOutput();
        shutOut = true;
    }

    private  boolean isConnected()
    {
        return connected || oldImpl;
    }

    private  boolean isBound()
    {
        return bound || oldImpl;
    }

    private  boolean isClosed()
    {
        synchronized (closeLock)
{
            return closed;
        }
    }

    private  boolean isInputShutdown()
    {
        return shutIn;
    }

    private  boolean isOutputShutdown()
    {
        return shutOut;
    }

    private static com.example.socket.MockSocketImplFactory factory = null;

}
