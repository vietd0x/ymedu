using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Net.Sockets; // for listeners and sockets
using System.Text;
using System.Threading;
using System.Windows.Forms;

namespace _03_multithread
{
    public partial class Form1 : Form
    {
        TcpListener tcpListener;
        Socket socketForClient;
        NetworkStream networkStream;
        StreamReader streamReader;

        //Use a separate thread for each command so that the
        //server commands can run concurrently instead of blocking
        Thread th_message, th_beep;

        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Shown(object sender, EventArgs e)
        {
            this.Hide();
            tcpListener = new TcpListener(System.Net.IPAddress.Any, 4444);
            tcpListener.Start();
            RunServer();
        }
        private void RunServer()
        {
            socketForClient = tcpListener.AcceptSocket();
            networkStream = new NetworkStream(socketForClient);
            streamReader = new StreamReader(networkStream);

            try
            {
                string line;
                //Command loop, LastIndexOf is to search within
                //the Network Stream for any command strings
                //sent by the Client

                while (true)
                {
                    line = "";
                    line = streamReader.ReadLine();
                    if (line.LastIndexOf("m") >= 0)
                    {
                        th_message = new Thread(new ThreadStart(MessageCommand));
                        th_message.Start();
                    }
                    if (line.LastIndexOf("b") >= 0)
                    {
                        th_beep = new Thread(new ThreadStart(BeepCommand));
                        th_beep.Start();
                    }
                    if (line.LastIndexOf("q") >= 0)
                        throw new Exception(); //so that it will be caught below and gracefully close
                }//end while
            }
            catch (Exception exc)
            {
                streamReader.Close();
                networkStream.Close();
                socketForClient.Close();
                System.Environment.Exit(System.Environment.ExitCode);
            }
        }
        
        // perform tasks
        private void MessageCommand()
        {
            MessageBox.Show("Hello World");
        }
        private void BeepCommand()
        {
            Console.Beep(500, 2000);
        }
    }
}
